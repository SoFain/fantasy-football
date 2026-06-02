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
Before deploying, make sure that Google Cloud Build, Artifact Registry, BigQuery, and Cloud Run APIs are enabled in your project:
```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    bigquery.googleapis.com
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

---

## 5. Deploy to Google Cloud Run
Deploy the compiled container to Cloud Run, attaching the newly configured service account and restricting access to authenticated users:
```bash
gcloud run deploy nfl-studio-dashboard \
    --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/nfl-studio-repo/nfl-studio-app:latest \
    --region=us-central1 \
    --service-account=nfl-studio-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
    --port=8501 \
    --no-allow-unauthenticated
```

### Explanations of Flags:
- `--image`: The location of your Docker image in Artifact Registry.
- `--service-account`: Links the IAM roles (BigQuery Admin) directly to the running container instance (enabling passwordless, fileless BigQuery access).
- `--port=8501`: Sets the container ingress port to align with Streamlit's default port.
- `--no-allow-unauthenticated`: Restricts access so only authenticated IAM users in your GCP project can access the dashboard. (Change this to `--allow-unauthenticated` if you want to make it publicly accessible).

---

## 6. Accessing the App
Once the deployment finishes, the terminal will print the Service URL:
`Service URL: https://nfl-studio-dashboard-xxxxxx.a.run.app`

Double-click or navigate to that URL in your browser to access the dashboard!
