#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

IMAGE_NAME="dj-tango-ci-build"
ARTIFACT_DIR="ci/artifacts"

mkdir -p "$ARTIFACT_DIR"

echo "Building Docker image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" -f ci/Dockerfile .

echo "Creating temporary container to extract built artifact..."
CONTAINER_ID=$(docker create "$IMAGE_NAME")

echo "Copying executable to $ARTIFACT_DIR..."
docker cp "$CONTAINER_ID":/app/dist/DJTango "$ARTIFACT_DIR/DJTango"

docker rm "$CONTAINER_ID" >/dev/null
chmod +x "$ARTIFACT_DIR/DJTango"

echo "Build complete. Artifact available at $ARTIFACT_DIR/DJTango"
