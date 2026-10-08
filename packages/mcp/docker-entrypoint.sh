#!/bin/sh
set -eu

exec setpriv --reuid=appuser --regid=appuser --init-groups "$@"
