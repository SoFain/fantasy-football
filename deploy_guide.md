# Google Cloud Run Deployment Guide: Pigskin

This document provides step-by-step instructions for containerizing the Pigskin warehouse jobs and deploying them securely to Google Cloud Run Jobs.

There is no service to deploy. The Streamlit dashboard was retired; the image runs `src/job_runner.py` per execution and exits.

---

## Prerequisites
1. Installed **Google Cloud SDK (gcloud CLI)** on your local machine.
2. Authenticated CLI environment:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```
3. Set your active Google Cloud project ID:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

---

## 1. Enable Required GCP Service APIs
Before deploying, make sure that Google Cloud Build, Artifact Registry, BigQuery, Secret Manager, Vertex AI Search, and Cloud Run APIs are enabled in your project:
```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    bigquery.googleapis.com \
    secretmanager.googleapis.com \
    discoveryengine.googleapis.com
```

---

## 2. Create Artifact Registry Repository
Create a Docker repository in Artifact Registry to store your container image:
```bash
gcloud artifacts repositories create nfl-studio-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Repository for NFL Data Studio container images"
```

---

## 3. Build & Publish Using Google Cloud Build
Google Cloud Build packages the local `Dockerfile` and pushes one immutable Artifact Registry tag. Do not deploy `latest`; production and staging releases must use explicit tags.

Generate a staging tag:

```powershell
$tag = .\venv\Scripts\python.exe scripts\build_image_tag.py --channel staging
$shortSha = (git rev-parse --short=12 HEAD).Trim()
gcloud builds submit `
    --config cloudbuild.yaml `
    --substitutions "_IMAGE_TAG=$tag,_COMMIT_HASH=$shortSha,_VERSION_LABEL=$tag"
```

Generate a production candidate tag:

```powershell
$tag = .\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod-candidate
$shortSha = (git rev-parse --short=12 HEAD).Trim()
gcloud builds submit `
    --config cloudbuild.yaml `
    --substitutions "_IMAGE_TAG=$tag,_COMMIT_HASH=$shortSha,_VERSION_LABEL=$tag"
```

Generate a production release tag only after the production release is approved:

```powershell
$releaseId = "r2026.06.16"
$tag = .\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod --release-id $releaseId
$shortSha = (git rev-parse --short=12 HEAD).Trim()
gcloud builds submit `
    --config cloudbuild.yaml `
    --substitutions "_IMAGE_TAG=$tag,_COMMIT_HASH=$shortSha,_VERSION_LABEL=$tag"
```

Tag patterns:

- Staging: `staging-<short_sha>-<timestamp>`
- Production candidate: `prod-candidate-<short_sha>-<timestamp>`
- Production release: `prod-<short_sha>-<release_id>`

The `cloudbuild.yaml` file no longer tags or pushes `latest`.

---

## 4. Set Up Service Account IAM Permissions
Cloud Run services run under a designated identity. Instead of uploading JSON files, we utilize **Application Default Credentials (ADC)**. 

By default, Cloud Run uses the Compute Engine default service account. However, we recommend creating a dedicated service account with the minimal BigQuery roles:

1. Create a service account:
   ```bash
   gcloud iam service-accounts create nfl-studio-sa \
       --description="Service account for running the NFL Data Studio on Cloud Run" \
       --display-name="nfl-studio-sa"
   ```
2. Assign the BigQuery roles to allow data loading and dataset management:
   ```bash
   # Assign BigQuery Admin (needed to create datasets and load tables)
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:nfl-studio-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/bigquery.admin"
   ```
3. Allow the Cloud Run service account to read the Gemini secret from Secret Manager:
   ```bash
   gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
       --member="serviceAccount:nfl-studio-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```
4. Allow the Cloud Run service account to search the configured Vertex AI Search app:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:nfl-studio-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/discoveryengine.viewer"
   ```

`roles/secretmanager.secretAccessor` is enough for runtime access. The service does not need Secret Manager Editor.

---

## 5. Deploy Cloud Run Jobs

Create one Cloud Run Job per job name. Jobs run to completion and exit; they have no ingress port and no public URL.

```bash
gcloud run jobs create pigskin-materialize-analytics     --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/nfl-studio-repo/nfl-studio-app:latest     --region=us-central1     --service-account=nfl-studio-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com     --set-env-vars=BQ_PROJECT=YOUR_PROJECT_ID,EXTERNAL_SEARCH_PROVIDER=vertex_ai_search,EXTERNAL_SEARCH_DAILY_LIMIT=25,EXTERNAL_SEARCH_MAX_RESULTS=3,VERTEX_AI_SEARCH_ENGINE_ID=YOUR_VERTEX_SEARCH_ENGINE_ID     --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest     --args=--job-name,materialize-analytics     --max-retries=1     --task-timeout=3600s
```

Execute it:

```bash
gcloud run jobs execute pigskin-materialize-analytics --region=us-central1 --wait
```

Override arguments per execution without redeploying:

```bash
gcloud run jobs execute pigskin-materialize-analytics --region=us-central1 --args=--job-name,materialize-analytics,--season,2026
```

`src/cloud_run_jobs.py:cloud_run_job_name` maps a job name to its Cloud Run Job name, so keep the `pigskin-` prefix convention.

### Explanations of Flags:
- `--image`: The location of your Docker image in Artifact Registry.
- `--service-account`: Links the IAM roles directly to the running container instance, enabling passwordless, fileless BigQuery access.
- `--set-env-vars`: Pins the warehouse project, selects Vertex AI Search, caps external verification at 25 requests per UTC day, and limits each search to 3 stored results. You can provide `VERTEX_AI_SEARCH_SERVING_CONFIG` instead of `VERTEX_AI_SEARCH_ENGINE_ID` if you want to pass the full serving config resource name.
- `--set-secrets`: Injects Secret Manager values without storing keys in code or the container image.
- `--args`: The job name and any job-specific flags, passed to the `src.job_runner` entrypoint.
- `--task-timeout`: Raise this for long ingestion or backtest jobs. The default is too short for a full pipeline run.

There is no `--allow-unauthenticated` decision to make: jobs are not network-reachable. Access is controlled entirely by who may execute the job and what the service account may do.

### Staging-Only Compatibility Flag
Phase 15.3 promotes only Trade Lab player history to staging. Production defaults remain unchanged.

Enable it on the staging Cloud Run service only:

```powershell
gcloud run services update <staging-service-name> `
    --region <region> `
    --set-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY=true
```

Do not set the other `USE_COMPAT_*` flags until their staged QA reports explicitly approve promotion. Roll back the staging flag with:

```powershell
gcloud run services update <staging-service-name> `
    --region <region> `
    --remove-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY
```

### External Verification Cost Controls
- Default cap: 25 external search requests per UTC day.
- Absolute hard cap in code: 99 external search requests per UTC day.
- Default stored results: 3 per request.
- Absolute hard result cap in code: 5 per request.
- `verify-external-context` calls Vertex AI Search `servingConfigs.search` only. It does not request generative answers.
- Set `EXTERNAL_SEARCH_DAILY_LIMIT=0` to disable external verification entirely.
- Keep the Vertex AI Search data store limited to a curated football source set instead of general web search.

---

## 6. Checking Job Results

Executions are visible in the Cloud Run Jobs console and in BigQuery:

```sql
SELECT job_run_id, job_name, status, started_at, finished_at, row_count, error_message
FROM `YOUR_PROJECT_ID.fantasy_football_brain.cloud_run_job_runs`
ORDER BY started_at DESC
LIMIT 20
```

Every execution records a row through `src/cloud_run_jobs.py`. A job that fails before reaching the recorder will appear in Cloud Run logs but not in this table.
