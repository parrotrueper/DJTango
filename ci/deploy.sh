#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=/dev/null
. ci/functions.sh


IMAGE_NAME="ttvttm-dev"
ARTIFACT_DIR="ci/artifacts"

mkdir -p "$ARTIFACT_DIR"

info "Running development checks before deploy"

run ./dev-check.sh

info "Building Docker image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" -f ci/Dockerfile .

info "Creating temporary container to extract built artifact..."
CONTAINER_ID=$(docker create "$IMAGE_NAME")

info "Copying executable to $ARTIFACT_DIR..."
docker cp "$CONTAINER_ID":/app/dist/ttvttm "$ARTIFACT_DIR/ttvttm"

docker rm "$CONTAINER_ID" >/dev/null
chmod +x "$ARTIFACT_DIR/ttvttm"

info "Build complete. Artifact available at $ARTIFACT_DIR/ttvttm"
