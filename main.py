from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv
import os

from prometheus_fastapi_instrumentator import Instrumentator
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from models import Server, Metric, Deployment, Incident
from routers import servers, metrics, deployments, incidents
from detection import check_cpu_usage

load_dotenv()

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    await init_beanie(
        database=client.helios,
        document_models=[Server, Metric, Deployment, Incident],
    )
    print("✅ Connected to MongoDB Atlas")

    scheduler.add_job(check_cpu_usage, "interval", seconds=15)
    scheduler.start()
    print("✅ Detect engine running (checking every 15s)")

    yield  # app runs here

    scheduler.shutdown()
    client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(servers.router)
app.include_router(metrics.router)
app.include_router(deployments.router)
app.include_router(incidents.router)

Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Project Helios"}