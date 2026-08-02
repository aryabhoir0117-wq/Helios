import asyncio
import docker
from datetime import datetime
from models import Incident
from prom_client import query_prometheus
from learn import generate_post_incident_report

SAFE_ACTIONS = {"restart_container"}
CPU_THRESHOLD = 0.5         # same threshold as detection.py
VERIFY_DELAY_SECONDS = 20    # wait for container to restart + report fresh metrics


async def execute_recovery(incident: Incident):
    if incident.recommended_action not in SAFE_ACTIONS:
        return incident  # guardrail: not an auto-executable action

    client = docker.from_env()
    container_name = incident.server_id

    try:
        container = client.containers.get(container_name)
        container.restart()
        incident.action_result = "success"
    except Exception as e:
        incident.action_result = f"failed: {e}"
        incident.action_taken = "restart_container"
        incident.action_timestamp = datetime.utcnow()
        await incident.save()
        return incident  # don't attempt verify if restart itself failed

    incident.action_taken = "restart_container"
    incident.action_timestamp = datetime.utcnow()
    await incident.save()

    # Verify: wait for the container to settle, then re-check CPU
    await asyncio.sleep(VERIFY_DELAY_SECONDS)

    try:
        results = await query_prometheus(
            f'rate(container_cpu_usage_seconds_total{{job="cadvisor", name="{container_name}"}}[1m])'
        )
        if results:
            post_cpu = float(results[0]["value"][1])
            incident.post_action_cpu = post_cpu
            incident.resolved = post_cpu < CPU_THRESHOLD
            if incident.resolved:
                incident.status = "resolved"
                try:
                    incident.post_incident_report = await generate_post_incident_report(incident)
                except Exception as e:
                    print(f"⚠️ Report generation failed: {e}")
                    incident.post_incident_report = None
        else:
            incident.post_action_cpu = None
            incident.resolved = False
    except Exception as e:
        print(f"⚠️ Verify step failed: {e}")
        incident.post_action_cpu = None
        incident.resolved = False

    await incident.save()
    return incident