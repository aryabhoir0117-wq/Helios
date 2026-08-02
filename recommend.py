def recommend_action(reason_code: str, predicted_trend: str) -> str:
    """
    Deterministic mapping from a fixed reason_code + predicted_trend to a
    bounded action set. reason_code is always one of:
    "recent_deployment", "restart_loop", "no_pattern"
    """
    if reason_code == "recent_deployment":
        return "rollback_deployment"

    if reason_code == "restart_loop":
        return "restart_container"

    if predicted_trend == "rising":
        return "restart_container"

    if predicted_trend in ("stable", "falling"):
        return "monitor_only"

    return "monitor_only"  # covers "unknown" / "insufficient_data"