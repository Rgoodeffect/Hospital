#!/bin/bash
# The base image links app assets into /home/frappe/frappe-bench/assets at
# build time via `bench build`, but that doesn't reliably survive into the
# containers started from this image (bench-root/assets isn't a declared
# VOLUME, but the base image's own `sites` VOLUME declaration appears to
# affect how later RUN layers under the bench root get committed). Ensure
# fertility_suite's asset symlink exists on every container start instead
# of depending on the image build having preserved it.
set -e

ln -sfn /home/frappe/frappe-bench/apps/fertility_suite/fertility_suite/public \
	/home/frappe/frappe-bench/assets/fertility_suite 2>/dev/null || true

exec /usr/local/bin/entrypoint.sh "$@"
