"""
One-off script to directly test execute_recovery() end-to-end,
bypassing the trend-detection guardrail (predicted_trend must be "rising"
for recommend_action() to ever return "restart_container" naturally,
which our constant-load stress test never produces).

Run this manually: python test_recovery.py
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from models import Server, Metric, Deployment, Incident
from recovery import execute_recovery

load_dotenv()

# CHANGE THIS to a real running container's short ID from `docker ps`
# e.g. if docker ps shows "175beb9108e5" for server-1-cpu, use that.
TEST_CONTAINER_ID = "52abe4bd3e5f06b5fb7e0a02ab77c8933b7605532dcaf9ba24b6c88b8910062c"


async def main():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    await init_beanie(
        database=client.helios,
        document_models=[Server, Metric, Deployment, Incident],
    )

    incident = Incident(
        server_id=f"/docker/{TEST_CONTAINER_ID}",
        title="TEST: manual recovery trigger",
        cpu_value=0.99,
        recommended_action="restart_container",
    )
    await incident.insert()
    print(f"Created test incident: {incident.id}")

    result = await execute_recovery(incident)

    print("\n--- execute_recovery() result ---")
    print(f"action_taken:    {result.action_taken}")
    print(f"action_result:   {result.action_result}")
    print(f"post_action_cpu: {result.post_action_cpu}")
    print(f"resolved:        {result.resolved}")
    print(f"status:          {result.status}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())