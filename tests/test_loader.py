import pytest
import yaml
from pathlib import Path
from pct.loader import load_suite


def write_yaml(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "suite.yaml"
    p.write_text(yaml.dump(data))
    return str(p)


def test_loads_valid_suite(tmp_path):
    path = write_yaml(tmp_path, {
        "suite": "test_suite",
        "prompt": "Do something.",
        "cases": [{"name": "case1", "mock_response": "ok"}],
    })
    suite = load_suite(path)
    assert suite["suite"] == "test_suite"
    assert len(suite["cases"]) == 1


def test_missing_suite_field(tmp_path):
    path = write_yaml(tmp_path, {
        "prompt": "Do something.",
        "cases": [{"name": "case1"}],
    })
    with pytest.raises(ValueError, match="suite"):
        load_suite(path)


def test_missing_prompt_field(tmp_path):
    path = write_yaml(tmp_path, {
        "suite": "test_suite",
        "cases": [{"name": "case1"}],
    })
    with pytest.raises(ValueError, match="prompt"):
        load_suite(path)


def test_missing_cases_field(tmp_path):
    path = write_yaml(tmp_path, {
        "suite": "test_suite",
        "prompt": "Do something.",
    })
    with pytest.raises(ValueError, match="cases"):
        load_suite(path)


def test_empty_cases_list(tmp_path):
    path = write_yaml(tmp_path, {
        "suite": "test_suite",
        "prompt": "Do something.",
        "cases": [],
    })
    with pytest.raises(ValueError, match="cases"):
        load_suite(path)


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_suite("/nonexistent/path/suite.yaml")
