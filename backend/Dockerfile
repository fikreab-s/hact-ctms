# =============================================================================
# HACT CTMS — Django Backend Dockerfile
# Multi-stage build | Python 3.12 | Non-root user | Production-ready
# =============================================================================
FROM --platform=linux/amd64 python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for psycopg2 and general build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (21 CFR Part 11 — principle of least privilege)
RUN groupadd --gid 1000 hact && \
    useradd --uid 1000 --gid hact --create-home --shell /bin/bash hact

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R hact:hact /app

# Make entrypoint executable (fix Windows CRLF line endings)
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Switch to non-root user
USER hact

# Expose port
EXPOSE 8000

# Default entrypoint — use bash explicitly to avoid CRLF shebang issues
ENTRYPOINT ["bash", "/app/entrypoint.sh"]

