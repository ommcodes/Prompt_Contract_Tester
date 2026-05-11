import yaml


def load_suite(path: str) -> dict:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML must be a mapping at the top level")

    for field in ("suite", "prompt", "cases"):
        if field not in data:
            raise ValueError(f"{path}: missing required field '{field}'")

    if not isinstance(data["cases"], list) or len(data["cases"]) == 0:
        raise ValueError(f"{path}: 'cases' must be a non-empty list")

    return data
