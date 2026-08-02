from statistics import mean
from collections import Counter
from models import Incident
from explanation import _call_groq, _call_gemini


async def get_incident_history(server_id: str) -> list[Incident]:
    """
    All resolved incidents for a given server, oldest -> newest.
    This is the dataset Learn's pattern analysis will run over.
    """
    return await Incident.find(
        Incident.server_id == server_id,
        Incident.resolved == True
    ).sort(+Incident.action_timestamp).to_list()


async def get_pattern_summary(server_id: str) -> dict:
    """
    Aggregated stats over a server's resolved incident history.
    """
    incidents = await get_incident_history(server_id)

    if not incidents:
        return {
            "server_id": server_id,
            "total_resolved": 0,
            "message": "No resolved incident history yet."
        }

    total = len(incidents)

    # restart_container success rate
    restart_attempts = [i for i in incidents if i.action_taken == "restart_container"]
    restart_successes = [i for i in restart_attempts if i.action_result == "success"]
    restart_success_rate = (
        len(restart_successes) / len(restart_attempts) if restart_attempts else None
    )

    # most common root cause
    root_causes = [i.root_cause for i in incidents if i.root_cause]
    most_common_root_cause = Counter(root_causes).most_common(1)[0][0] if root_causes else None

    # average time-to-resolve (investigated_at -> action_timestamp)
    durations = [
        (i.action_timestamp - i.investigated_at).total_seconds()
        for i in incidents
        if i.action_timestamp and i.investigated_at
    ]
    avg_time_to_resolve_seconds = mean(durations) if durations else None

    # recurrence: how many incidents this server has had, period
    recurrence_count = total

    return {
        "server_id": server_id,
        "total_resolved": total,
        "restart_success_rate": restart_success_rate,
        "most_common_root_cause": most_common_root_cause,
        "avg_time_to_resolve_seconds": avg_time_to_resolve_seconds,
        "recurrence_count": recurrence_count,
    }


async def generate_post_incident_report(incident: Incident) -> str:
    """
    Plain-English summary of a resolved incident: what happened,
    what was tried, what worked. Same AI pattern as explanation.py.
    """
    prompt = f"""
Summarize this resolved incident in plain English, 3-4 sentences, for someone
reviewing an incident log. Cover: what happened, what was tried, what the result was.
Output only the summary itself, no preamble, no alternate versions.

Server: {incident.server_id}
Root cause: {incident.root_cause or "unknown"}
Explanation at detection time: {incident.explanation or "n/a"}
Action taken: {incident.action_taken or "none"}
Action result: {incident.action_result or "unknown"}
CPU before action: {incident.cpu_value}
CPU after action: {incident.post_action_cpu}
Resolved: {incident.resolved}
"""
    try:
        return await _call_groq(prompt)
    except Exception as e:
        print(f"⚠️ Groq failed ({e}), falling back to Gemini")
        try:
            return await _call_gemini(prompt)
        except Exception as e2:
            print(f"⚠️ Gemini also failed ({e2})")
            raise