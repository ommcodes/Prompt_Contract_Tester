import json
import re


def extract_json(text: str) -> str:
    """Strip markdown code fences and return the raw JSON string."""
    text = text.strip()
    # Match ```json ... ``` or ``` ... ```
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        return fence.group(1).strip()
    return text


def parse_json(text: str) -> dict | list | None:
    try:
        return json.loads(extract_json(text))
    except (json.JSONDecodeError, TypeError):
        return None


def get_path(data: dict | list, path: str) -> tuple[bool, object]:
    """Traverse a dot-separated path. Returns (found, value)."""
    parts = path.split(".")
    current = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def has_path(data: dict | list, path: str) -> bool:
    found, _ = get_path(data, path)
    return found
