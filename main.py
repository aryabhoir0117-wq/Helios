from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv
import os

from models import Server, Metric, Deployment, Incident

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    await init_beanie(
        database=client.helios,  # database name — creates it automatically if it doesn't exist
        document_models=[Server, Metric, Deployment, Incident],
    )
    print("✅ Connected to MongoDB Atlas")
    yield  # app runs here
    client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Project Helios"}