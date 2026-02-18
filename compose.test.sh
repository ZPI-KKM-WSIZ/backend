#!/bin/bash
server_uuid="$(uuidgen | cut -d'-' -f1)"
export BACKEND_HOSTNAME="zpi-backend-$server_uuid"
export SERVER_ID=$server_uuid
docker compose -f docker-compose.test.yaml up -d
