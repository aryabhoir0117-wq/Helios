from predict import predict_trend
import httpx
from datetime import datetime
from models import Incident
from investigation import investigate_incident
from explanation import explain_root_cause
from prom_client import query_prometheus
from recommend import recommend_action

CPU_THRESHOLD = 0.5


async def check_cpu_usage():

    results = await query_prometheus(
        'rate(container_cpu_usage_seconds_total{job="cadvisor", id!="/"}[1m])'
    )

    DEBUG_METRICS = False

    for result in results:
        if DEBUG_METRICS:
           print("RAW METRIC LABELS:", result["metric"])

        container_id = result["metric"].get("id", "unknown")
        cpu_rate = float(result["value"][1])

        if cpu_rate > CPU_THRESHOLD:

            existing = await Incident.find_one(
                Incident.server_id == container_id,
                Incident.status == "open"
            )

            if existing:
                # Re-evaluate trend + recommendation as more data comes in
                prediction = await predict_trend(container_id)
                existing.predicted_trend = prediction["predicted_trend"]
                existing.predicted_cpu_in_2min = prediction["predicted_cpu_in_2min"]

                # Need reason_code again for recommend_action — re-derive from root_cause step
                reason_code, _ = await investigate_incident(existing)
                existing.recommended_action = recommend_action(reason_code, prediction["predicted_trend"])

                await existing.save()
                print(
                    f"🔄 Re-evaluated {container_id}: trend={existing.predicted_trend}, "
                    f"action={existing.recommended_action}"
                )
                continue

            incident = Incident(
                server_id=container_id,
                title=f"High CPU usage detected: {cpu_rate:.2f} cores",
                cpu_value=cpu_rate
            )
            await incident.insert()

            reason_code, cause_text = await investigate_incident(incident)
            incident.root_cause = cause_text
            incident.investigated_at = datetime.utcnow()
            await incident.save()

            prediction = await predict_trend(container_id)
            incident.predicted_trend = prediction["predicted_trend"]
            incident.predicted_cpu_in_2min = prediction["predicted_cpu_in_2min"]
            await incident.save()

            incident.recommended_action = recommend_action(reason_code, prediction["predicted_trend"])
            await incident.save()

            try:
                explanation = await explain_root_cause(incident.title, cause_text)
                incident.explanation = explanation
                await incident.save()
            except Exception as e:
                print(f"❌ Explanation step failed entirely: {e}")
                incident.explanation = "Explanation unavailable (AI service error)."
                await incident.save()

            print(
                f"🚨 Incident created for {container_id}: {cpu_rate:.2f} cores\n"
                f"🔎 Cause: {cause_text}\n"
                f"📈 Trend: {prediction['predicted_trend']}\n"
                f"🛠️ Action: {incident.recommended_action}\n"
                f"🗣️ Explanation: {incident.explanation}"
            )