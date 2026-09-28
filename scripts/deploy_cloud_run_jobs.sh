#!/usr/bin/env bash
set -euo pipefail

SUPPORTED_JOBS=(
  "ingest-nflverse"
  "ingest-sleeper-news"
  "ingest-sleeper-league"
  "ingest-context-events"
  "ingest-market-values"
  "ingest-college-stats"
  "materialize-analytics"
  "generate-pigskin-rankings"
  "generate-evidence-packets"
  "run-projections"
  "run-backtests"
  "validate-warehouse"
  "verify-external-context"
  "generate-content-briefs"
  "grade-claims"
)

PROJECT="${CLOUD_RUN_PROJECT:-${BQ_PROJECT:-fantasy-football-498121}}"
REGION="${CLOUD_RUN_REGION:-us-central1}"
IMAGE="${CLOUD_RUN_JOBS_IMAGE:-}"
SERVICE_ACCOUNT="${CLOUD_RUN_JOB_SERVICE_ACCOUNT:-}"
DATASET="${BQ_DATASET:-fantasy_football_brain}"
JOB_NAME=""
DRY_RUN=false
RUN_AFTER_DEPLOY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --run-after-deploy) RUN_AFTER_DEPLOY=true; shift ;;
    --project) PROJECT="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    --image) IMAGE="$2"; shift 2 ;;
    --service-account) SERVICE_ACCOUNT="$2"; shift 2 ;;
    --job-name) JOB_NAME="$2"; shift 2 ;;
    --dataset) DATASET="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$IMAGE" ]]; then
  echo "Missing --image or CLOUD_RUN_JOBS_IMAGE." >&2
  exit 2
fi

contains_job() {
  local candidate="$1"
  for job in "${SUPPORTED_JOBS[@]}"; do
    [[ "$job" == "$candidate" ]] && return 0
  done
  return 1
}

if [[ -n "$JOB_NAME" ]] && ! contains_job "$JOB_NAME"; then
  echo "Unsupported job name: $JOB_NAME" >&2
  exit 2
fi

run_or_preview() {
  printf '%q ' "$@"
  printf '\n'
  if [[ "$DRY_RUN" != "true" ]]; then
    "$@"
  fi
}

JOBS_TO_DEPLOY=("${SUPPORTED_JOBS[@]}")
if [[ -n "$JOB_NAME" ]]; then
  JOBS_TO_DEPLOY=("$JOB_NAME")
fi

echo "Project: $PROJECT"
echo "Region: $REGION"
echo "Dataset: $DATASET"
echo "Image: $IMAGE"
echo "Dry run: $DRY_RUN"
echo "Run after deploy: $RUN_AFTER_DEPLOY"

for job in "${JOBS_TO_DEPLOY[@]}"; do
  command=(
    gcloud run jobs deploy "$job"
    --project "$PROJECT"
    --region "$REGION"
    --image "$IMAGE"
    --command python
    --args "-m,src.job_runner,--job-name,$job,--project,$PROJECT,--dataset,$DATASET"
    --set-env-vars "BQ_PROJECT=$PROJECT,BQ_DATASET=$DATASET"
  )
  if [[ -n "$SERVICE_ACCOUNT" ]]; then
    command+=(--service-account "$SERVICE_ACCOUNT")
  fi
  run_or_preview "${command[@]}"

  if [[ "$RUN_AFTER_DEPLOY" == "true" ]]; then
    run_or_preview gcloud run jobs execute "$job" --project "$PROJECT" --region "$REGION"
  fi
done
