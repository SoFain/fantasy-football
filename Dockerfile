# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies (exclude pyinstaller for clean web-hosting containers)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source files
COPY app.py validate.py ./
COPY src/ ./src/
COPY data/ ./data/

# Set Streamlit environment variables
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

ARG COMMIT_HASH
ENV APP_VERSION=$COMMIT_HASH

# Expose port (Cloud Run will override this dynamically via the PORT environment variable)
EXPOSE 8501

# Execute app, dynamically binding to the port injected by Cloud Run or defaulting to 8501
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.fileWatcherType=none"]
