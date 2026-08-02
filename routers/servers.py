from fastapi import APIRouter, HTTPException
from models import Server

router = APIRouter(prefix="/servers", tags=["Servers"])

@router.post("/")
async def create_server(name: str, ip_address: str = None):
    server = Server(name=name, ip_address=ip_address)
    await server.insert()
    return server

@router.get("/")
async def list_servers():
    return await Server.find_all().to_list()

@router.patch("/{server_id}")
async def update_server(server_id: str, container_name: str = None, status: str = None, ip_address: str = None):
    server = await Server.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if container_name is not None:
        server.container_name = container_name
    if status is not None:
        server.status = status
    if ip_address is not None:
        server.ip_address = ip_address

    await server.save()
    return server
@router.delete("/{server_id}")
async def delete_server(server_id: str):
    server = await Server.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    await server.delete()
    return {"deleted": server_id}