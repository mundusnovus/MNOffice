#!/bin/sh
set -eu
: "${JWT_SECRET:?Set the same JWT secret in Cloud and Office}"
if [ "${#JWT_SECRET}" -lt 32 ]; then echo 'JWT_SECRET must have at least 32 characters' >&2; exit 1; fi
exec /entrypoint.sh "$@"
