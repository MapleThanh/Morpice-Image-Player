def parse_session_duration(duration_str):
    """Parse session duration string into structured data."""
    # Remove the session name if it's included
    if ": " in duration_str:
        duration_str = duration_str.split(": ", 1)[1]  # Get everything after ": "

    segments = []
    for segment in duration_str.split(" + "):
        parts = segment.split("x")
        if len(parts) != 2:
            continue
        try:
            count = int(parts[0])
            duration_unit = parts[1].strip()
            segment_type = "active"

            if "break" in duration_unit:
                segment_type = "break"
                duration_unit = duration_unit.replace(" break", "")

            if "min" in duration_unit:
                duration = int(duration_unit.replace("min", "")) * 60
                unit = "minutes"
            else:
                duration = int(duration_unit.replace("sec", ""))
                unit = "seconds"

            segments.append((count, duration, unit, segment_type))
        except ValueError:
            print(f"Skipping invalid segment: {segment}")  # Debugging

    return segments
