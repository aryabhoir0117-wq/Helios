from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional

class Server(Document):
    name: str
    ip_address: Optional[str] = None
    status: str = "unknown"  # "healthy" | "warning" | "critical"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "servers"  # actual MongoDB collection name


class Metric(Document):
    server_id: str
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "metrics"


class Deployment(Document):
    server_id: str
    commit_hash: str
    image_tag: str
    status: str  # "success" | "failed"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "deployments"


class Incident(Document):
    server_id: str
    title: str
    root_cause: Optional[str] = None
    status: str = "open"  # "open" | "investigating" | "resolved"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    class Settings:
        name = "incidents"