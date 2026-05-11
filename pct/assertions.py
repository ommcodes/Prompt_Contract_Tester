from pct.json_utils import parse_json, get_path


def _values_equal(actual, expected) -> bool:
    """Compare loosely: booleans, numbers, strings."""
    if actual == expected:
        return True
    # Handle bool/string cross-comparison ("true" == True)
    if isinstance(actual, bool):
        return str(actual).lower() == str(expected).lower()
    if isinstance(expected, bool):
        return str(actual).lower() == str(expected).lower()
    # Numeric string comparison
    try:
        return float(actual) == float(expected)
    except (TypeError, ValueError):
        pass
    return str(actual) == str(expected)


def evaluate_response(response_text: str, expect: dict) -> dict:
    errors: list[str] = []
    parsed = None

    # --- valid_json ---
    if expect.get("valid_json"):
        parsed = parse_json(response_text)
        if parsed is None:
            errors.append("valid_json: response is not valid JSON")
            return {"passed": False, "errors": errors, "parsed_json": None}

    # Parse anyway if assertions or other checks need it
    if parsed is None and (
        expect.get("required_keys")
        or expect.get("forbidden_keys")
        or expect.get("assertions")
        or expect.get("forbidden_values")
    ):
        parsed = parse_json(response_text)

    # --- required_keys ---
    for key in expect.get("required_keys", []):
        if not isinstance(parsed, dict) or key not in parsed:
            errors.append(f"required_keys: missing key '{key}'")

    # --- forbidden_keys ---
    for key in expect.get("forbidden_keys", []):
        if isinstance(parsed, dict) and key in parsed:
            errors.append(f"forbidden_keys: key '{key}' must not be present")

    # --- refusal_contains ---
    for phrase in expect.get("refusal_contains", []):
        if phrase.lower() not in response_text.lower():
            errors.append(f"refusal_contains: expected '{phrase}' in response")

    # --- assertions ---
    for assertion in expect.get("assertions", []):
        path = assertion.get("path", "")
        found, value = get_path(parsed or {}, path)

        if "equals" in assertion:
            if not found:
                errors.append(f"assertions: path '{path}' not found")
            elif not _values_equal(value, assertion["equals"]):
                errors.append(
                    f"assertions: '{path}' equals '{value}', expected '{assertion['equals']}'"
                )

        if "type" in assertion:
            expected_type = assertion["type"]
            if not found:
                errors.append(f"assertions: path '{path}' not found")
            else:
                type_ok = _check_type(value, expected_type)
                if not type_ok:
                    errors.append(
                        f"assertions: '{path}' has type {type(value).__name__}, expected {expected_type}"
                    )

        if "contains" in assertion:
            if not found:
                errors.append(f"assertions: path '{path}' not found")
            elif assertion["contains"] not in str(value):
                errors.append(
                    f"assertions: '{path}' does not contain '{assertion['contains']}'"
                )

    # --- forbidden_values ---
    for rule in expect.get("forbidden_values", []):
        path = rule.get("path", "")
        banned = rule.get("values", [])
        found, value = get_path(parsed or {}, path)
        if found and value in banned:
            errors.append(
                f"forbidden_values: '{path}' = '{value}' is in banned list {banned}"
            )

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "parsed_json": parsed,
    }


def _check_type(value, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return False
