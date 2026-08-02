import httpx

PROMETHEUS_URL = "http://localhost:9090"


async def query_prometheus(promql: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": promql}
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]["result"]

async def query_prometheus_range(promql: str, start: float, end: float, step: str = "30s"):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={"query": promql, "start": start, "end": end, "step": step}
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]["result"]    