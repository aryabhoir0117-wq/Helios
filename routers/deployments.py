from fastapi import APIRouter, HTTPException
from models import Deployment

router = APIRouter(prefix="/deployments", tags=["Deployments"])

@router.post("/")
async def log_deployment(server_id: str, commit_hash: str, image_tag: str, status: str = "success"):
    deployment = Deployment(server_id=server_id, commit_hash=commit_hash, image_tag=image_tag, status=status)
    await deployment.insert()
    return deployment

@router.get("/")
async def list_deployments():
    return await Deployment.find_all().sort(-Deployment.timestamp).to_list()
@router.delete("/{deployment_id}")
async def delete_deployment(deployment_id: str):
    deployment = await Deployment.get(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    await deployment.delete()
    return {"deleted": deployment_id}