#!/bin/bash
export BACKEND_HOSTNAME="zpi-backend-$(uuidgen | cut -d'-' -f1)"
docker compose -f docker-compose.prod.yaml up -d
