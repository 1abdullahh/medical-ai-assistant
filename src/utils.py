import json
import re


def clean_json_text(raw_text):
    """
    Removes ```json fences, stray backticks, and surrounding whitespace
    from a model's raw text response so it can be parsed as JSON.
    """
    if raw_text is None:
        return ""

    text = raw_text.strip()
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def safe_parse_json(raw_text):
    """
    Safely parses the model's response into a Python dict.
    Never raises an exception - always returns a (data, error) tuple.

    Returns:
        (dict, None) on success
        (None, str) on failure, where str is a friendly error message
    """
    cleaned = clean_json_text(raw_text)

    if not cleaned:
        return None, "The model returned an empty response."

    try:
        data = json.loads(cleaned)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Could not parse the AI response as JSON ({e})."


def get_urgency_color(level):
    """Maps an urgency level string to a simple color name for UI styling."""
    colors = {
        "LOW": "green",
        "MEDIUM": "orange",
        "HIGH": "red",
        "EMERGENCY": "red",
    }
    return colors.get((level or "").upper(), "gray")