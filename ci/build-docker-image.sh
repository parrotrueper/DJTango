#!/usr/bin/env bash
# Exit on error
set -euo pipefail

#-------------------------------------------
# Build the Docker image. Invoke as "ci/build-docker-image.sh".
#-------------------------------------------

# shellcheck source=/dev/null
. ci/functions.sh

RESULT_IMAGE="ttvttm-dev"
DOCKERFILE="ci/Dockerfile"
VERBOSE="no"
USE_CACHE="yes"

info "generate compose files"
#run ci/generate-compose-files.sh

bld_cmd="docker build"

if [[ "${VERBOSE:?}" == "yes" ]]; then
	bld_cmd+=" --progress=plain"
fi

if [[ "${USE_CACHE:?}" == "no" ]]; then
	bld_cmd+=" --no-cache"
fi
bld_cmd+=" --file ${DOCKERFILE:?}"
bld_cmd+=" -t ${RESULT_IMAGE:?}"
# build context
bld_cmd+=" ."

#echo "${bld_cmd}"
eval "${bld_cmd}"

