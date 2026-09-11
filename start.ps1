Write-Host "Activating virtual environment..."
& .H\Scripts\Activate.ps1

Write-Host "Starting Docker stack (Prometheus + cAdvisor)..."
docker compose up -d

Write-Host "Recreating test-load containers (server-1-cpu, server-2-mem, server-3-idle)..."

docker rm -f server-1-cpu server-2-mem server-3-idle 2>$null

docker run -d `
  --name server-1-cpu `
  --cpus="1" `
  polinux/stress `
  stress --cpu 2 --timeout 300s

docker run -d `
  --name server-2-mem `
  --memory="256m" `
  polinux/stress `
  stress --vm 1 --vm-bytes 200M --timeout 300s

docker run -d `
  --name server-3-idle `
  alpine `
  sleep 300

Write-Host "Checking container status..."
docker ps --format "table {{.Names}}\t{{.Status}}"

Write-Host ""
Write-Host "Starting FastAPI backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000