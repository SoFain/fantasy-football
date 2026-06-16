# Google Cloud Run Deployment Guide: NFL Data Studio

This document provides step-by-step instructions for containerizing the Streamlit dashboard and deploying it securely to Google Cloud Run.

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
Google Cloud Build will package your code using the local `Dockerfile` (optimized for Streamlit) and push it directly to your Artifact Registry repository:
```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/nfl-studio-repo/nfl-studio-app:latest
```
*(Make sure to replace `YOUR_PROJECT_ID` with your actual Google Cloud Project ID).*

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

## 5. Deploy to Google Cloud Run
Deploy the compiled container to Cloud Run, attaching the newly configured service account, wiring the Gemini secret into environment variables, pinning the BigQuery project, setting conservative external verification limits, and restricting access to authenticated users:
```bash
gcloud run deploy nfl-studio-dashboard \
    --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/nfl-studio-repo/nfl-studio-app:latest \
    --region=us-central1 \
    --service-account=nfl-studio-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars=BQ_PROJECT=YOUR_PROJECT_ID,EXTERNAL_SEARCH_PROVIDER=vertex_ai_search,EXTERNAL_SEARCH_DAILY_LIMIT=25,EXTERNAL_SEARCH_MAX_RESULTS=3,VERTEX_AI_SEARCH_ENGINE_ID=YOUR_VERTEX_SEARCH_ENGINE_ID \
    --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest \
    --port=8501 \
    --no-allow-unauthenticated
```

### Explanations of Flags:
- `--image`: The location of your Docker image in Artifact Registry.
- `--service-account`: Links the IAM roles (BigQuery Admin) directly to the running container instance (enabling passwordless, fileless BigQuery access).
- `--set-env-vars`: Pins the warehouse project, selects Vertex AI Search, caps external verification at 25 requests per UTC day, and limits each search to 3 stored results. You can provide `VERTEX_AI_SEARCH_SERVING_CONFIG` instead of `VERTEX_AI_SEARCH_ENGINE_ID` if you want to pass the full serving config resource name.
- `--set-secrets`: Injects Secret Manager values without storing keys in code or the container image.
- `--port=8501`: Sets the container ingress port to align with Streamlit's default port.
- `--no-allow-unauthenticated`: Restricts access so only authenticated IAM users in your GCP project can access the dashboard. (Change this to `--allow-unauthenticated` if you want to make it publicly accessible).

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
- Default app cap: 25 external search requests per UTC day.
- Absolute hard cap in code: 99 external search requests per UTC day.
- Default stored results: 3 per request.
- Absolute hard result cap in code: 5 per request.
- The app calls Vertex AI Search `servingConfigs.search` only. It does not request generative answers.
- Set `EXTERNAL_SEARCH_DAILY_LIMIT=0` to disable external verification entirely.
- Keep the Vertex AI Search data store limited to a curated football source set instead of general web search.

---

## 6. Accessing the App
Once the deployment finishes, the terminal will print the Service URL:
`Service URL: https://nfl-studio-dashboard-xxxxxx.a.run.app`

Double-click or navigate to that URL in your browser to access the dashboard!
