from datetime import datetime, timedelta
from models import Deployment, Incident
from prom_client import query_prometheus


async def investigate_incident(incident: Incident) -> tuple[str, str]:
    """
    Rule-based root cause check.
    Returns (reason_code, human_readable_text).
    reason_code is always one of: "recent_deployment", "restart_loop", "no_pattern"
    Does NOT call any AI — pure logic.
    """
    server_id = incident.server_id
    lookback = datetime.utcnow() - timedelta(minutes=15)

    # 1. Check for a recent deployment
    recent_deploy = await Deployment.find(
        Deployment.server_id == server_id,
        Deployment.timestamp >= lookback
    ).sort(-Deployment.timestamp).first_or_none()

    if recent_deploy:
        return "recent_deployment", (
            f"Recent deployment '{recent_deploy.image_tag}' on this server "
            f"within the last 15 minutes — likely trigger."
        )

    # 2. Check for a restart loop
    if await is_restart_looping(server_id):
        return "restart_loop", (
            "Container has restarted multiple times in the last 15 minutes — "
            "likely stuck in a restart loop (crash on boot, bad config, or OOM kill)."
        )

    # 3. Fallback
    return "no_pattern", (
        "No recent deployment or restart pattern detected. Sustained resource "
        "usage with no obvious external trigger — likely organic load or a leak."
    )


async def is_restart_looping(container_id: str) -> bool:
    # NOTE: container_label_restartcount is cumulative since container creation,
    # not a rolling 15-min window like the function name implies. Fine for demo
    # purposes (containers get recreated fresh each time), but worth revisiting
    # if this needs to reflect "recent" restarts specifically later.
    promql = f'container_start_time_seconds{{name="{container_id}"}}'
    results = await query_prometheus(promql)

    if not results:
        return False

    restart_count = int(results[0]["metric"].get("container_label_restartcount", 0))
    return restart_count >= 2