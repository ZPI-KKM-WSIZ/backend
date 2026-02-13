#!/bin/bash
export BACKEND_HOSTNAME="zpi-backend-$(uuidgen | cut -d'-' -f1)"
docker compose -f docker-compose.test.yaml up -d
