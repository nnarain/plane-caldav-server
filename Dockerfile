FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies and Caddy
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    debian-keyring \
    debian-archive-keyring \
    apt-transport-https \
    gpg \
    curl && \
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg && \
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list && \
    && apt-get install -y libnss3-tools \
    apt-get install -y caddy && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .
COPY Caddyfile /app/Caddyfile

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
    PASSWORD="" \
    HOST="127.0.0.1" \
    PORT="8080" \
    HTTPS_PORT="8443"


# Create entrypoint script
COPY <<EOF /app/entrypoint.sh
#!/bin/sh
set -e

# Build command with optional Plane arguments
CMD="python -m plane_caldav_server.server --host \$HOST --port \$PORT --storage-folder \$STORAGE_FOLDER --user \$USER --htpasswd-file /app/htpasswd"

# Add password if provided
if [ -n "\$PASSWORD" ]; then
    CMD="\$CMD --password \$PASSWORD"
fi

if [ -n "\$PLANE_URL" ] && [ -n "\$API_KEY" ]; then
    CMD="\$CMD --plane-url \$PLANE_URL --api-key \$API_KEY --workspace \$WORKSPACE"
fi

echo "Starting plane caldav server with command: \$CMD"
\$CMD &

# Wait for the server to start
sleep 2

# Start Caddy server for HTTPS
echo "Starting Caddy HTTPS proxy..."
echo "HTTP:  http://0.0.0.0:5232"
echo "HTTPS: https://0.0.0.0:\$HTTPS_PORT"
exec caddy run --config /app/Caddyfile --adapter caddyfile
EOF

RUN chmod +x /app/entrypoint.sh

# Expose ports
EXPOSE 5232 8443

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
