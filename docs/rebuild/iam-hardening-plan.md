# IAM Hardening Plan

This plan defines the intended least-privilege service account model. It does not apply live IAM changes.

## Principles

- Runtime identities should not have deploy permissions.
- Deploy identities can have Cloud Run developer or admin permissions, but should not be used by jobs at runtime.
- Prefer dataset-level BigQuery permissions over broad project data permissions.
- Grant Secret Manager access per secret and per service account.
- Scheduler should invoke jobs through a narrow invoker identity.

## Service Accounts

| Service account | Purpose | Minimum roles |
| --- | --- | --- |
| `streamlit-dashboard-sa` | Streamlit Cloud Run service | Project `roles/bigquery.jobUser`; dataset viewer or editor only for admin metadata that the UI must write; Secret Accessor only for request-time secrets. |
| `ingestion-jobs-sa` | nflverse, Sleeper, market, college, and context ingestion jobs | Project `roles/bigquery.jobUser`; dataset `roles/bigquery.dataEditor`; Secret Accessor only for external API secrets used by ingestion. |
| `materialization-jobs-sa` | analytics and compatibility mart jobs | Project `roles/bigquery.jobUser`; dataset `roles/bigquery.dataEditor`; no LLM secrets by default. |
| `ranking-jobs-sa` | Pigskin ranking generation | Project `roles/bigquery.jobUser`; dataset `roles/bigquery.dataEditor`; Secret Accessor for `GEMINI_API_KEY`. |
| `evidence-jobs-sa` | evidence packet and content brief generation | Project `roles/bigquery.jobUser`; dataset `roles/bigquery.dataEditor`; Secret Accessor only if a future step calls an external or LLM service. |
| `validation-jobs-sa` | warehouse validation | Project `roles/bigquery.jobUser`; dataset viewer for read-only validations or editor if validation result recording is enabled. |
| `backtest-jobs-sa` | backtesting jobs | Project `roles/bigquery.jobUser`; dataset `roles/bigquery.dataEditor`; no secret access by default. |
| `claim-grading-jobs-sa` | claim grading and scorecards | Project `roles/bigquery.jobUser`; dataset `roles/bigquery.dataEditor`; no secret access by default. |
| `scheduler-invoker-sa` | Cloud Scheduler invoker | Cloud Run Job invoke permission only for approved jobs. |

## Deploy Identity

The operator or CI identity that deploys Cloud Run services and jobs may need:

- Cloud Run Developer or Admin
- Artifact Registry Reader or Writer, depending on build flow
- Service Account User for target runtime service accounts

That identity should not be used as a job runtime identity.

## Dataset Roles

Suggested BigQuery grants:

- UI read-only paths: dataset `roles/bigquery.dataViewer`
- Admin metadata writes: dataset `roles/bigquery.dataEditor` on the operational dataset
- Ingestion and materialization jobs: dataset `roles/bigquery.dataEditor`
- Validation jobs: dataset `roles/bigquery.dataViewer` unless result tables are written

All identities that submit BigQuery jobs need project `roles/bigquery.jobUser`.

## Secret Manager Roles

Grant `roles/secretmanager.secretAccessor` only on the needed secret.

Examples:

- `ranking-jobs-sa` can access `GEMINI_API_KEY`.
- `streamlit-dashboard-sa` should access `GEMINI_API_KEY` only if the dashboard is still making request-time Gemini calls.
- ingestion identities get only the external API keys they call.

## Scheduler Invoker

`scheduler-invoker-sa` should be able to invoke only approved Cloud Run Jobs. It should not have BigQuery data roles and should not have Secret Manager access.

## Rollout Checklist

1. Create runtime service accounts.
2. Grant project `roles/bigquery.jobUser`.
3. Grant dataset permissions per job class.
4. Grant secret access per secret and service account.
5. Deploy jobs with the correct service account.
6. Configure Scheduler to use `scheduler-invoker-sa`.
7. Run `validate-warehouse` first.
8. Review `cloud_run_job_runs` and Cloud Run logs.

No live IAM change is authorized by this document.
