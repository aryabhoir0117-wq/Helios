from fastapi import APIRouter, HTTPException
from models import Metric

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.post("/")
async def log_metric(server_id: str, cpu_percent: float, ram_percent: float, disk_percent: float):
    metric = Metric(server_id=server_id, cpu_percent=cpu_percent, ram_percent=ram_percent, disk_percent=disk_percent)
    await metric.insert()
    return metric

@router.get("/history/{server_id}")
async def get_metric_history(server_id: str, limit: int = 50):
    return await Metric.find(Metric.server_id == server_id).sort(-Metric.timestamp).limit(limit).to_list()
@router.delete("/{metric_id}")
async def delete_metric(metric_id: str):
    metric = await Metric.get(metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    await metric.delete()
    return {"deleted": metric_id}