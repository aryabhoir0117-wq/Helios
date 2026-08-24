#!/bin/bash
set -e

echo "Activating virtual environment..."
source .H/bin/activate

echo "Starting Docker stack (Prometheus + cAdvisor)..."
docker compose up -d

echo "Checking container status..."
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "If server-1-cpu / server-2-mem / server-3-idle are missing or Exited, recreate them manually."
echo ""

echo "Starting FastAPI backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000
