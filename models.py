from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional

class Server(Document):
    name: str
    ip_address: Optional[str] = None
    status: str = "unknown"  # "healthy" | "warning" | "critical"
    container_name: Optional[str] = None  # Docker container this server maps to, for Recover step
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "servers"


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
    status: str = "open"
    recommended_action: str | None = None
    cpu_value: float | None = None
    predicted_trend: str | None = None
    predicted_cpu_in_2min: float | None = None
    root_cause: str | None = None
    explanation: str | None = None
    investigated_at: datetime | None = None
    action_taken: str | None = None
    action_timestamp: datetime | None = None
    action_result: str | None = None
    post_action_cpu: float | None = None
    resolved: bool | None = None
    post_incident_report: str | None = None
    
    class Settings:
        name = "incidents"