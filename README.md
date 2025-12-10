# Plane CalDav Server

This is a CalDav proxy for [Plane Project Management](https://plane.so/) allowing any CalDav client to access the Plane task list.

## Docker Image

Docker images are automatically built and published to GitHub Container Registry on every push to the main branch and on version tags.

### Pull the Image

```bash
# Pull the latest version
docker pull ghcr.io/nnarain/plane-caldav-server:latest

# Pull a specific version (when tagged)
docker pull ghcr.io/nnarain/plane-caldav-server:v1.0.0
```

### Run the Container

```bash
# Create a directory for storing CalDAV collections
mkdir -p collections

# Run the container
docker run -d \
  -p 5232:5232 \
  -e PLANE_URL="https://your-plane-instance.com" \
  -e API_KEY="your-api-key" \
  -e WORKSPACE="your-workspace" \
  -e USER="your-username" \
  -v $(pwd)/collections:/app/collections \
  ghcr.io/nnarain/plane-caldav-server:latest
```

### Environment Variables

- `PLANE_URL`: URL of your Plane instance
- `API_KEY`: Your Plane API key
- `WORKSPACE`: Plane workspace name (default: "default")
- `STORAGE_FOLDER`: Storage folder for CalDAV collections (default: "/app/collections")
- `USER`: CalDAV username (default: "user")
- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: "5232")
