# Daily Pigskin chain, 07:30 ET leg: board refresh -> publish -> site import.
#
# Supersedes the main checkout's daily_publish_and_import.ps1 by adding the
# automated board refresh in front. Full chain:
#   07:00 ingest-sleeper-news (Cloud Run)  - the single /players fetch
#   07:15 detect-player-changes (Cloud Run)
#   07:30 this task:
#     1. run_daily_board_refresh.py --apply   (the runbook, fail-closed)
#     2. publish_public_rankings.py --publish (carry-forward datasets)
#     3. IONOS site import via run_remote_php
#
# Refresh exit policy:
#   0 -> boards refreshed; publish them.
#   1 -> a PRE-WRITE gate tripped (tests, coverage, or a formula-preservation
#        guardrail like the QB24 cutline). Boards untouched; publish the
#        last-approved state so the manifest and coaching dataset stay fresh.
#        The gate output in the log is an owner-review item, not an error.
#   3+ -> failure AFTER writes began. Publication is skipped per the runbook
#        Recovery section and the task reports failure.
#
# Scheduled task: PigskinDailyPublishImport (daily 07:30, machine TZ = Eastern).
# Remove with:  schtasks /delete /tn "PigskinDailyPublishImport" /f
# Run manually: powershell -NoProfile -ExecutionPolicy Bypass -File "E:\Fantasy Football\scripts\daily_pigskin_chain.ps1"
#
# Branch reconciliation 2026-07-26: the platform worktree merged into the codex
# line, so the chain now runs entirely from the main checkout ($branchRoot = $root).

$ErrorActionPreference = 'Stop'
$root = 'E:\Fantasy Football'
$branchRoot = $root
$cbs = 'E:\cbs-league-history'
$logDir = Join-Path $root 'output\daily-publish'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
try {
    Get-ChildItem $logDir -Filter '*.log' |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } |
        Remove-Item -Force -ErrorAction Stop
} catch {}
$log = Join-Path $logDir ("chain-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))

function Write-Log([string]$message) {
    ("{0} {1}" -f (Get-Date -Format 'o'), $message) | Add-Content -Path $log -Encoding utf8
}

function Invoke-Logged([string]$label, [string]$exe, [string]$argumentString, [string]$workDir) {
    Write-Log "start: $label"
    $out = [IO.Path]::GetTempFileName()
    $err = [IO.Path]::GetTempFileName()
    $proc = Start-Process -FilePath $exe -ArgumentList $argumentString -WorkingDirectory $workDir `
        -NoNewWindow -Wait -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
    Get-Content $out -ErrorAction SilentlyContinue | Add-Content -Path $log -Encoding utf8
    Get-Content $err -ErrorAction SilentlyContinue | Add-Content -Path $log -Encoding utf8
    Remove-Item $out, $err -Force -Confirm:$false
    Write-Log ("end: {0} exit={1}" -f $label, $proc.ExitCode)
    return $proc.ExitCode
}

$refreshExit = Invoke-Logged 'daily-board-refresh' "$root\venv\Scripts\python.exe" `
    ('"{0}\scripts\run_daily_board_refresh.py" --apply' -f $branchRoot) $root
if ($refreshExit -eq 0) {
    Write-Log 'board refresh complete; publishing the new boards'
} elseif ($refreshExit -eq 1) {
    Write-Log 'BOARD REFRESH GATE TRIPPED (no writes). Publishing last-approved boards; the gate output above is an owner-review item.'
} else {
    Write-Log "BOARD REFRESH FAILED after writes began (exit=$refreshExit); skipping publish and import per runbook Recovery."
    exit 1
}

# Stage 1b: the refresh emits fresh dataset artifacts (player situation, market
# context). Upload each immutable object (content-addressed: a re-upload of
# identical bytes fails the precondition harmlessly), then hand the manifest
# entries to the publisher. Any artifact missing (gate-tripped day, Sleeper API
# hiccup) is skipped and the publisher carries that dataset forward unchanged.
$publisherArgs = ('"{0}\scripts\publish_public_rankings.py" --publish --gcloud-auth' -f $root)
foreach ($datasetId in @('player_situation', 'market_context')) {
    $entryPath = Join-Path $branchRoot ("build\feeds\{0}.manifest-entry.json" -f $datasetId)
    $objectPath = Join-Path $branchRoot ("build\feeds\{0}.json" -f $datasetId)
    if ((Test-Path $entryPath) -and (Test-Path $objectPath)) {
        try {
            $entry = Get-Content $entryPath -Raw | ConvertFrom-Json
            $null = Invoke-Logged ("upload-{0}-object" -f $datasetId) 'gcloud' `
                ('storage cp "{0}" "gs://fantasy-football-498121-public-rankings/{1}" --content-type="application/json; charset=utf-8" --cache-control="public, max-age=31536000, immutable" --if-generation-match=0' -f $objectPath, $entry.object) $root
            # A nonzero exit here is expected when the object already exists;
            # content addressing guarantees identical bytes, so proceed either way.
            $publisherArgs = $publisherArgs + (' --dataset-entry "{0}"' -f $entryPath)
            Write-Log ('{0} dataset entry attached: {1}' -f $datasetId, $entry.object)
        } catch {
            Write-Log ('{0} dataset skipped (unreadable entry): {1}' -f $datasetId, $_.Exception.Message)
        }
    } else {
        Write-Log ('{0} dataset artifacts absent; publisher will carry the prior dataset forward.' -f $datasetId)
    }
}

$publishExit = Invoke-Logged 'publish-public-rankings' "$root\venv\Scripts\python.exe" $publisherArgs $root
if ($publishExit -ne 0) {
    Write-Log 'PUBLISH FAILED; skipping site import so the site never imports a partial publish.'
    exit 1
}

$importExit = Invoke-Logged 'ionos-site-import' 'C:\Python314\python.exe' `
    ('"{0}\scripts\run_remote_php.py" --file "{1}\scripts\trigger_site_rankings_import.php"' -f $cbs, $root) $cbs
if ($importExit -ne 0) {
    Write-Log 'IMPORT FAILED; the published feed is live but the site did not refresh.'
    exit 1
}

Write-Log 'done: chain succeeded'
exit 0
