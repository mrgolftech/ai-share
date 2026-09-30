def classify_temperature(temp_c: float) -> str:
    """Return the safety state for a measured temperature."""

    # Intentional training bug:
    # the exact critical threshold is currently classified incorrectly.
    if temp_c > 85.0:
        return "critical"
    if temp_c >= 75.0:
        return "warning"
    return "normal"
