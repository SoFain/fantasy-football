# Secret Manager Plan

This plan defines how the Cloud Run service and Cloud Run Jobs should receive secrets. It does not create or rotate live secrets.

## Principles

- Never commit service account JSON, private keys, `.env` files, or API keys.
- Prefer local Application Default Credentials for development.
- Bind secrets into Cloud Run services and jobs from Secret Manager.
- Grant `roles/secretmanager.secretAccessor` only to service accounts that need each secret.
- Fail clearly when a required secret is missing.

## Current Secrets

| Secret | Used by | Notes |
| --- | --- | --- |
| `GEMINI_API_KEY` | Pigskin ranking generation, optional LLM workflows | Required only where Gemini is called. |

## Future Secrets

Expected future adapters may need:

- external search provider keys
- paid rankings or ADP provider keys
- odds provider keys
- route participation provider keys
- weather provider keys if a paid tier is adopted

Each new adapter should document:

- secret name
- owning job
- required service account access
- missing-secret behavior
- rotation process

## Local Development

Use Application Default Credentials:

```powershell
gcloud auth application-default login
```

Do not place service account JSON in the repo. If a temporary credential file is required for one-off debugging, keep it outside the repo and verify it is ignored.

## Cloud Run Service Binding

The Streamlit service should receive only secrets needed for request-time behavior. Avoid giving the dashboard secrets that are only needed by long-running jobs.

Example operator command:

```powershell
gcloud run services update nfl-studio-dashboard `
  --region us-central1 `
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest
```

Use this only when the service truly needs the secret.

## Cloud Run Job Binding

Bind secrets at the job level when a job needs them.

Example for ranking generation:

```powershell
gcloud run jobs update generate-pigskin-rankings `
  --region us-central1 `
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest
```

Do not pass secrets through dashboard JSON args or non-secret environment overrides. `src/cloud_run_jobs.py` refuses sensitive env override names.

## Rotation

1. Add a new secret version in Secret Manager.
2. Leave job bindings pointed at `latest` unless a pinned version is required.
3. Run a dry-run or low-risk validation path.
4. Run the smallest live job that requires the secret.
5. Disable old versions after the new version is confirmed.
6. Record the rotation in project notes or the relevant phase report.

## Missing Secret Validation

Missing secret behavior should be tested by the owning job, not by Streamlit request-time code.

Expected behavior:

- dry-run paths do not require the secret
- live LLM or external API paths fail before writing incomplete output
- failures are recorded to job metadata with `error_message`
- secrets are not rendered in Streamlit or logs
