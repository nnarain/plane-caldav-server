FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .
COPY htpasswd /app/htpasswd

# Install the package
RUN pip install --no-cache-dir -e .

# Create collections directory
RUN mkdir -p /app/collections

# Environment variables with defaults
ENV API_KEY="" \
    PLANE_URL="" \
    WORKSPACE="default" \
    STORAGE_FOLDER="/app/collections" \
    USER="user" \
    HOST="0.0.0.0" \
    PORT="5232"

# Expose CalDAV port
EXPOSE 5232

# Create entrypoint script
COPY <<EOF /app/entrypoint.sh
#!/bin/sh
set -e

# Build command with optional Plane arguments
CMD="python -m plane_caldav_server.server --host \$HOST --port \$PORT --storage-folder \$STORAGE_FOLDER --user \$USER --htpasswd-file /app/htpasswd"

if [ -n "\$PLANE_URL" ] && [ -n "\$API_KEY" ]; then
    CMD="\$CMD --plane-url \$PLANE_URL --api-key \$API_KEY --workspace \$WORKSPACE"
fi

echo "Starting server with command: \$CMD"
exec \$CMD
EOF

RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
