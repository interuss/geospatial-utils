#!/usr/bin/env bash

set -eo pipefail

# Find and change to repo root directory
OS=$(uname)
if [[ "$OS" == "Darwin" ]]; then
	# OSX uses BSD readlink
	BASEDIR="$(dirname "$0")"
else
	BASEDIR=$(readlink -e "$(dirname "$0")")
fi
cd "${BASEDIR}/.." || exit 1

(
cd geospatial-utils || exit 1
make image
)

if [ "$CI" == "true" ]; then
  docker_args=""
else
  docker_args="-it"
fi

# shellcheck disable=SC2086
docker run ${docker_args} --name geospatial-utils \
  --rm \
  --network interop_ecosystem_network \
  --add-host=host.docker.internal:host-gateway \
  -u "$(id -u):$(id -g)" \
  -e PYTHONBUFFERED=1 \
  -v ./geospatial-utils/.cache:/app/geospatial-utils/.cache \
  -v ./geospatial-utils/output:/app/geospatial-utils/output \
  -w /app/geospatial-utils \
  interuss/geospatial-utils \
  uv run main.py ${@}