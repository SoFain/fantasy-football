Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SupportedJobs = @(
    "ingest-nflverse",
    "ingest-sleeper-news",
    "ingest-sleeper-league",
    "ingest-context-events",
    "ingest-market-values",
    "ingest-college-stats",
    "materialize-analytics",
    "generate-pigskin-rankings",
    "generate-evidence-packets",
    "run-projections",
    "run-backtests",
    "validate-warehouse",
    "verify-external-context",
    "generate-content-briefs",
    "grade-claims"
)

$Project = $env:CLOUD_RUN_PROJECT
if (-not $Project) { $Project = $env:BQ_PROJECT }
if (-not $Project) { $Project = "fantasy-football-498121" }
$Region = $env:CLOUD_RUN_REGION
if (-not $Region) { $Region = "us-central1" }
$Image = $env:CLOUD_RUN_JOBS_IMAGE
$ServiceAccount = $env:CLOUD_RUN_JOB_SERVICE_ACCOUNT
$Dataset = $env:BQ_DATASET
if (-not $Dataset) { $Dataset = "fantasy_football_brain" }
$JobName = ""
$DryRun = $false
$RunAfterDeploy = $false

for ($i = 0; $i -lt $args.Count; $i++) {
    switch ($args[$i]) {
        "--dry-run" { $DryRun = $true }
        "--run-after-deploy" { $RunAfterDeploy = $true }
        "--project" { $i++; $Project = $args[$i] }
        "--region" { $i++; $Region = $args[$i] }
        "--image" { $i++; $Image = $args[$i] }
        "--service-account" { $i++; $ServiceAccount = $args[$i] }
        "--job-name" { $i++; $JobName = $args[$i] }
        "--dataset" { $i++; $Dataset = $args[$i] }
        default { throw "Unknown argument: $($args[$i])" }
    }
}

if (-not $Image) {
    throw "Missing --image or CLOUD_RUN_JOBS_IMAGE."
}

if ($JobName -and ($SupportedJobs -notcontains $JobName)) {
    throw "Unsupported job name: $JobName"
}

function Format-Command {
    param([string[]]$Command)
    return ($Command | ForEach-Object {
        if ($_ -match "\s") { "'" + ($_ -replace "'", "''") + "'" } else { $_ }
    }) -join " "
}

function Invoke-Or-Preview {
    param([string[]]$Command)
    Write-Host (Format-Command $Command)
    if (-not $DryRun) {
        & $Command[0] @($Command[1..($Command.Count - 1)])
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE"
        }
    }
}

$JobsToDeploy = if ($JobName) { @($JobName) } else { $SupportedJobs }

Write-Host "Project: $Project"
Write-Host "Region: $Region"
Write-Host "Dataset: $Dataset"
Write-Host "Image: $Image"
Write-Host "Dry run: $DryRun"
Write-Host "Run after deploy: $RunAfterDeploy"

foreach ($Job in $JobsToDeploy) {
    $DeployCommand = @(
        "gcloud", "run", "jobs", "deploy", $Job,
        "--project", $Project,
        "--region", $Region,
        "--image", $Image,
        "--command", "python",
        "--args", "-m,src.job_runner,--job-name,$Job,--project,$Project,--dataset,$Dataset",
        "--set-env-vars", "BQ_PROJECT=$Project,BQ_DATASET=$Dataset"
    )
    if ($ServiceAccount) {
        $DeployCommand += @("--service-account", $ServiceAccount)
    }
    Invoke-Or-Preview $DeployCommand

    if ($RunAfterDeploy) {
        $RunCommand = @("gcloud", "run", "jobs", "execute", $Job, "--project", $Project, "--region", $Region)
        Invoke-Or-Preview $RunCommand
    }
}
