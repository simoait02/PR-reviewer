#!/bin/sh
set -eu

docker_socket=/var/run/docker.sock

if [ -S "$docker_socket" ]; then
    socket_gid=$(stat -c '%g' "$docker_socket")
    socket_group=$(getent group "$socket_gid" | cut -d: -f1 || true)

    if [ -z "$socket_group" ]; then
        socket_group=docker-socket
        groupadd --gid "$socket_gid" "$socket_group"
    fi

    usermod --append --groups "$socket_group" appuser
fi

exec setpriv --reuid=appuser --regid=appuser --init-groups "$@"
