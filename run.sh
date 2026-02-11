#!/bin/bash
set -e

cd PATH_TO_PROJECT
export $(grep -v '^#' .env | xargs)

source venv/bin/activate

uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000
