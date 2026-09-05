#!/bin/bash
set -e

echo "Activating virtual environment..."
source .H/bin/activate

echo "Starting Docker stack (Prometheus + cAdvisor)..."
docker compose up -d

echo "Recreating test-load containers (server-1-cpu, server-2-mem, server-3-idle)..."

docker rm -f server-1-cpu server-2-mem server-3-idle 2>/dev/null || true

docker run -d \
  --name server-1-cpu \
  --cpus="1" \
  polinux/stress \
  stress --cpu 2 --timeout 300s

docker run -d \
  --name server-2-mem \
  --memory="256m" \
  polinux/stress \
  stress --vm 1 --vm-bytes 200M --timeout 300s

docker run -d \
  --name server-3-idle \
  alpine \
  sleep 300

echo "Checking container status..."
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "Starting FastAPI backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000