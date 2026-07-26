# Daily public-feed publish + site import (the 07:30 ET leg of the 7am chain).
#
# Chain: 07:00 ingest-sleeper-news (Cloud Run) -> 07:15 detect-player-changes
# (Cloud Run) -> 07:30 this task (local): publish the public rankings JSON feed,
# then trigger the IONOS site import over SSH.
#
# Runs locally because the import leg is inherently local: run_remote_php.py
# uses SSH credentials that live only on this machine, and the publisher's
# --gcloud-auth uses this machine's cached gcloud user login. The publish is
# idempotent (content-addressed objects; unchanged boards re-verify) and the
# import skips unchanged profiles by sha256, so a quiet day is a cheap no-op.
#
# Scheduled task: PigskinDailyPublishImport (daily 07:30, PC timezone = Eastern).
# Remove with:  schtasks /delete /tn "PigskinDailyPublishImport" /f
# Run manually: powershell -NoProfile -ExecutionPolicy Bypass -File "E:\Fantasy Football\scripts\daily_publish_and_import.ps1"

$ErrorActionPreference = 'Stop'
$root = 'E:\Fantasy Football'
$cbs = 'E:\cbs-league-history'
$logDir = Join-Path $root 'output\daily-publish'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
try {
    Get-ChildItem $logDir -Filter '*.log' |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } |
        Remove-Item -Force -ErrorAction Stop
} catch {}
$log = Join-Path $logDir ("publish-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))

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

$publishExit = Invoke-Logged 'publish-public-rankings' "$root\venv\Scripts\python.exe" `
    ('"{0}\scripts\publish_public_rankings.py" --publish --gcloud-auth' -f $root) $root
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

Write-Log 'done: publish + import succeeded'
exit 0
