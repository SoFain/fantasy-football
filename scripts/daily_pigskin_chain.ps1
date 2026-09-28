# Daily Pigskin chain, 07:30 ET leg: board refresh -> publish -> site import.
#
# Supersedes the main checkout's daily_publish_and_import.ps1 by adding the
# automated board refresh in front. Full chain:
#   07:00 ingest-sleeper-news (Cloud Run)  - the single /players fetch
#   07:15 detect-player-changes (Cloud Run)
#   07:30 this task:
#     1. run_daily_board_refresh.py --apply   (the runbook, fail-closed)
#     2. availability decisions + feed dataset (non-fatal, context only)
#     3. publish_public_rankings.py --publish (carry-forward datasets)
#     4. IONOS site import via run_remote_php
#
# Refresh failures always retain the previous public release and fail the task.
# Scheduled retries handle transient failures; never relabel old boards as fresh.
#
# Scheduled task: PigskinDailyPublishImport (daily 07:30 and 12:30 ET; two 30-minute retries).
# Remove with:  schtasks /delete /tn "PigskinDailyPublishImport" /f
# Run manually: powershell -NoProfile -ExecutionPolicy Bypass -File "E:\Fantasy Football\scripts\daily_pigskin_chain.ps1"
#
# Branch reconciliation 2026-07-26: the platform worktree merged into the codex
# line, so the chain now runs entirely from the main checkout ($branchRoot = $root).

$ErrorActionPreference = 'Stop'
$root = 'E:\Fantasy Football'
$env:CLOUDSDK_PYTHON = "$root\venv\Scripts\python.exe"
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

function Invoke-Logged([string]$label, [string]$exe, [string]$argumentString, [string]$workDir, [int]$timeoutSeconds = 0) {
    Write-Log "start: $label"
    $out = [IO.Path]::GetTempFileName()
    $err = [IO.Path]::GetTempFileName()
    if ($timeoutSeconds -gt 0) {
        # Bounded step: a hung process is killed and reported as exit 124.
        $proc = Start-Process -FilePath $exe -ArgumentList $argumentString -WorkingDirectory $workDir `
            -WindowStyle Hidden -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
        $null = $proc.Handle  # keeps ExitCode readable after exit
        if ($proc.WaitForExit($timeoutSeconds * 1000)) {
            $exitCode = $proc.ExitCode
        } else {
            # The venv python.exe is a launcher with a child interpreter: kill the whole tree.
            & taskkill.exe /PID $proc.Id /T /F 2>&1 | Out-Null
            $proc.WaitForExit(30000) | Out-Null
            Write-Log ("timeout: {0} killed after {1}s" -f $label, $timeoutSeconds)
            $exitCode = 124
        }
    } else {
        $proc = Start-Process -FilePath $exe -ArgumentList $argumentString -WorkingDirectory $workDir `
            -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
        $exitCode = $proc.ExitCode
    }
    Get-Content $out -ErrorAction SilentlyContinue | Add-Content -Path $log -Encoding utf8
    Get-Content $err -ErrorAction SilentlyContinue | Add-Content -Path $log -Encoding utf8
    Remove-Item $out, $err -Force -Confirm:$false -ErrorAction SilentlyContinue
    Write-Log ("end: {0} exit={1}" -f $label, $exitCode)
    return $exitCode
}

$season = (Get-Date).Year
if ((Get-Date).Month -lt 9) { $season-- }
$statsExit = Invoke-Logged 'current-season-stats' "$root\venv\Scripts\python.exe" `
    ('"{0}\scripts\refresh_current_season_stats.py" --season {1} --apply' -f $root, $season) $root
if ($statsExit -ne 0) {
    Write-Log 'STATS REFRESH FAILED; skipping ranking publication.'
    exit 1
}

$refreshExit = Invoke-Logged 'daily-board-refresh' "$root\venv\Scripts\python.exe" `
    ('"{0}\scripts\run_daily_board_refresh.py" --apply' -f $branchRoot) $root
if ($refreshExit -ne 0) {
    Write-Log "BOARD REFRESH FAILED (exit=$refreshExit); retaining the previous public release and reporting task failure."
    exit 1
}
Write-Log 'board refresh complete; publishing the new boards'

$gngStatsExit = Invoke-Logged 'current-gng-scoring' "$root\venv\Scripts\python.exe" `
    ('"{0}\scripts\inseason_gng_scoring.py" --season {1} --output "{0}\output\inseason-gng\{1}.json"' -f $root, $season) $root
if ($gngStatsExit -ne 0) { Write-Log 'GNG SCORING FAILED; retaining previous release.'; exit 1 }
$inseasonExit = Invoke-Logged 'inseason-ranking-horizons' "$root\venv\Scripts\python.exe" `
    ('"{0}\scripts\inseason_rankings.py" --season {1} --release-artifacts' -f $root, $season) $root
$seasonComplete = $inseasonExit -eq 20
if ($seasonComplete) {
    Write-Log 'Regular season complete; retaining the last in-season dataset while continuing core publication.'
} elseif ($inseasonExit -ne 0) { Write-Log 'IN-SEASON VALIDATION FAILED; retaining previous release.'; exit 1 }

# AI decision layer (docs/ai-decision-layer.md): availability decisions for every
# currently injured player, then the `availability` feed dataset. Context only,
# never a rank change, and never fatal: yesterday's artifacts are removed first,
# the script writes both artifacts only after schema validation (entry last), and
# when they are absent the upload loop skips the dataset and the publisher
# carries the previous availability object forward. Bounded at 15 minutes.
$availabilityArtifacts = @(
    (Join-Path $branchRoot 'build\feeds\availability.json'),
    (Join-Path $branchRoot 'build\feeds\availability.manifest-entry.json')
)
try {
    Remove-Item -LiteralPath $availabilityArtifacts -Force -ErrorAction SilentlyContinue
    $availabilityExit = Invoke-Logged 'availability-decisions' "$root\venv\Scripts\python.exe" `
        ('"{0}\scripts\run_availability_decisions.py" --live' -f $root) $root 900
    if ($availabilityExit -ne 0) {
        Write-Log "AVAILABILITY DECISIONS EXIT $availabilityExit; non-fatal. The dataset is attached only if its validated artifacts exist."
    }
} catch {
    Write-Log ("AVAILABILITY DECISIONS ERROR: {0}; non-fatal, the publisher carries the previous availability dataset forward." -f $_.Exception.Message)
    Remove-Item -LiteralPath $availabilityArtifacts -Force -ErrorAction SilentlyContinue
}

# Stage 1b: the refresh emits fresh dataset artifacts (player situation, market
# context). Upload each immutable object (content-addressed: a re-upload of
# identical bytes fails the precondition harmlessly), then hand the manifest
# entries to the publisher. Any artifact missing (gate-tripped day, Sleeper API
# hiccup) is skipped and the publisher carries that dataset forward unchanged.
$publisherArgs = ('"{0}\scripts\publish_public_rankings.py" --publish --gcloud-auth' -f $root)
foreach ($datasetId in @('player_situation', 'market_context', 'inseason_rankings', 'availability')) {
    if ($seasonComplete -and $datasetId -eq 'inseason_rankings') {
        Write-Log 'Skipping stale local in-season artifacts after season completion; public manifest carries the last dataset forward.'
        continue
    }
    $entryPath = Join-Path $branchRoot ("build\feeds\{0}.manifest-entry.json" -f $datasetId)
    $objectPath = Join-Path $branchRoot ("build\feeds\{0}.json" -f $datasetId)
    if ((Test-Path $entryPath) -and (Test-Path $objectPath)) {
        try {
            $entry = Get-Content $entryPath -Raw | ConvertFrom-Json
            $uploadExit = Invoke-Logged ("upload-{0}-object" -f $datasetId) 'gcloud.cmd' `
                ('storage cp "{0}" "gs://fantasy-football-498121-public-rankings/{1}" --content-type="application/json; charset=utf-8" --cache-control="public, max-age=31536000, immutable" --if-generation-match=0' -f $objectPath, $entry.object) $root
            if ($uploadExit -ne 0) {
                # An existing immutable object is safe only after readback.
                $verifyPath = [IO.Path]::GetTempFileName()
                try {
                    Invoke-WebRequest -UseBasicParsing -Uri ('https://storage.googleapis.com/fantasy-football-498121-public-rankings/{0}' -f $entry.object) -OutFile $verifyPath
                    if ((Get-FileHash -LiteralPath $verifyPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
                        throw 'Existing dataset object does not match its SHA-256.'
                    }
                } finally { Remove-Item -LiteralPath $verifyPath -Force }
            }
            $publisherArgs = $publisherArgs + (' --dataset-entry "{0}"' -f $entryPath)
            Write-Log ('{0} dataset entry attached: {1}' -f $datasetId, $entry.object)
        } catch {
            Write-Log ('{0} dataset upload failed: {1}' -f $datasetId, $_.Exception.Message)
            if ($datasetId -eq 'availability') {
                Write-Log 'availability upload failure is non-fatal; the publisher carries the previous availability dataset forward.'
                continue
            }
            exit 1
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
    Write-Log 'IONOS import failed once; retrying after 10 seconds.'
    Start-Sleep -Seconds 10
    $importExit = Invoke-Logged 'ionos-site-import-retry' 'C:\Python314\python.exe' `
        ('"{0}\scripts\run_remote_php.py" --file "{1}\scripts\trigger_site_rankings_import.php"' -f $cbs, $root) $cbs
    if ($importExit -ne 0) {
        Write-Log 'IMPORT FAILED twice; the published feed is live but the site did not refresh.'
        exit 1
    }
}

$verifyExit = Invoke-Logged 'verify-public-rankings' "$root\venv\Scripts\python.exe" `
    ('"{0}\scripts\verify_live_rankings.py"' -f $root) $root
if ($verifyExit -ne 0) {
    Write-Log 'PUBLIC VERIFICATION FAILED.'
    exit 1
}
Write-Log 'done: chain succeeded'
exit 0
