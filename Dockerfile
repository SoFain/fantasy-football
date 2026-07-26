# Pigskin warehouse jobs image.
#
# This image runs Cloud Run Jobs, not a web service. It has no HTTP listener and
# no UI; the Streamlit admin app was retired. Every job is invoked through
# src.job_runner, which records a row in cloud_run_job_runs per execution.
#
#   docker run <image> --job-name materialize-analytics --season 2026
#
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source files. bigquery/ and scripts/ ship so the
# validate-warehouse job can run migrations and validation SQL in-image.
COPY validate.py ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY bigquery/ ./bigquery/
COPY data/ ./data/
COPY docs/rebuild/live-2026-ranking-review-boards.md ./docs/rebuild/live-2026-ranking-review-boards.md
COPY docs/rebuild/pigskin-live-ranking-formula-context.md ./docs/rebuild/pigskin-live-ranking-formula-context.md

ARG COMMIT_HASH=unknown
ARG VERSION_LABEL=dev
ENV APP_VERSION=$VERSION_LABEL \
    APP_COMMIT=$COMMIT_HASH \
    PYTHONUNBUFFERED=1

# The job name is supplied per execution, so it is an argument rather than a
# baked-in command. Cloud Run Jobs override this via --args.
ENTRYPOINT ["python", "-m", "src.job_runner"]
CMD ["--help"]
