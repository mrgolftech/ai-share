def classify_temperature(temp_c: float) -> str:
    """Return the safety state for a measured temperature."""

    if temp_c > 85.0:
        return "critical"
    if temp_c >= 75.0:
        return "warning"
    return "normal"
