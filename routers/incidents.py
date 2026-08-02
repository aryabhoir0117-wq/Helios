from fastapi import APIRouter, HTTPException
from models import Incident
from recovery import execute_recovery
from learn import get_incident_history, get_pattern_summary

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("/")
async def create_incident(server_id: str, title: str):
    incident = Incident(server_id=server_id, title=title)
    await incident.insert()
    return incident

@router.get("/")
async def list_incidents(status: str = None):
    if status:
        return await Incident.find(Incident.status == status).to_list()
    return await Incident.find_all().to_list()

@router.post("/{incident_id}/recover")
async def recover_incident(incident_id: str):
    incident = await Incident.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    updated = await execute_recovery(incident)
    return updated

@router.get("/{incident_id}/report")
async def get_incident_report(incident_id: str):
    incident = await Incident.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not incident.post_incident_report:
        raise HTTPException(status_code=404, detail="No report generated for this incident (not yet resolved)")
    return {"incident_id": incident_id, "report": incident.post_incident_report}


@router.get("/servers/{server_id}/insights")
async def get_server_insights(server_id: str):
    return await get_pattern_summary(server_id)
    
@router.delete("/{incident_id}")
async def delete_incident(incident_id: str):
    incident = await Incident.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    await incident.delete()
    return {"deleted": incident_id}