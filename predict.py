import time
from prom_client import query_prometheus_range

RISING_THRESHOLD = 0.02   # cores/sec slope to call it "rising"
FALLING_THRESHOLD = -0.02


async def predict_trend(container_name: str) -> dict:
    """
    Looks at the last 15 minutes of CPU usage for a container and
    fits a simple straight-line trend to it. No ML — just least squares.
    """
    now = time.time()
    start = now - 15 * 60

    promql = f'rate(container_cpu_usage_seconds_total{{job="cadvisor", id="{container_name}"}}[1m])'    results = await query_prometheus_range(promql, start, now, step="30s")

    print(f"🔍 DEBUG predict_trend: promql={promql}")
    print(f"🔍 DEBUG predict_trend: results={results}")

    if not results:
        return {"predicted_trend": "unknown", "predicted_cpu_in_2min": None}

    all_points = []
    for series in results:
        all_points.extend(series.get("values", []))

    points = sorted(
        [(float(ts), float(v)) for ts, v in all_points],
        key=lambda p: p[0]
    )

    if len(points) < 4:
        return {"predicted_trend": "unknown", "predicted_cpu_in_2min": None}

    slope, _ = _linear_regression(points)
    print(f"🔍 DEBUG predict_trend: slope={slope}")

    if slope > RISING_THRESHOLD:
        trend = "rising"
    elif slope < FALLING_THRESHOLD:
        trend = "falling"
    else:
        trend = "stable"

    last_val = points[-1][1]

    if trend == "stable":
        predicted = round(last_val, 3)
    else:
        raw_predicted = last_val + slope * 120
        predicted = max(0.0, round(min(raw_predicted, last_val * 3), 3))

    return {"predicted_trend": trend, "predicted_cpu_in_2min": predicted}

def _linear_regression(points: list[tuple[float, float]]) -> tuple[float, float]:
    """Plain least-squares fit — dataset's small enough not to need numpy."""
    x0 = points[0][0]
    xs = [p[0] - x0 for p in points]
    ys = [p[1] for p in points]
    n = len(xs)
    mean_x, mean_y = sum(xs) / n, sum(ys) / n

    denom = sum((x - mean_x) ** 2 for x in xs)
    if denom == 0:
        return 0.0, mean_y

    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denom
    return slope, mean_y - slope * mean_x