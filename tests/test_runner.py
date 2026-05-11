import os
import pytest
from pathlib import Path
from pct.loader import load_suite
from pct.runner import run_suite
from pct.report import write_markdown_report


INVOICE_YAML = Path(__file__).parent / "invoice_extractor.yaml"
AGENT_YAML = Path(__file__).parent / "agent_tool_planner.yaml"


def test_invoice_suite_counts():
    suite = load_suite(str(INVOICE_YAML))
    summary = run_suite(suite, mock=True)
    assert summary["suite"] == "invoice_extractor"
    assert summary["total"] == 3
    assert summary["passed"] == 1
    assert summary["failed"] == 2


def test_invoice_first_case_passes():
    suite = load_suite(str(INVOICE_YAML))
    summary = run_suite(suite, mock=True)
    assert summary["cases"][0]["passed"] is True
    assert summary["cases"][0]["name"] == "extracts normal invoice"


def test_invoice_second_case_fails():
    suite = load_suite(str(INVOICE_YAML))
    summary = run_suite(suite, mock=True)
    assert summary["cases"][1]["passed"] is False


def test_invoice_third_case_fails():
    suite = load_suite(str(INVOICE_YAML))
    summary = run_suite(suite, mock=True)
    assert summary["cases"][2]["passed"] is False


def test_agent_suite_counts():
    suite = load_suite(str(AGENT_YAML))
    summary = run_suite(suite, mock=True)
    assert summary["suite"] == "agent_tool_planner"
    assert summary["total"] == 3
    assert summary["passed"] == 2
    assert summary["failed"] == 1


def test_agent_delete_case_fails():
    suite = load_suite(str(AGENT_YAML))
    summary = run_suite(suite, mock=True)
    delete_case = next(c for c in summary["cases"] if "delete" in c["name"])
    assert delete_case["passed"] is False


def test_report_written(tmp_path):
    suite = load_suite(str(INVOICE_YAML))
    summary = run_suite(suite, mock=True)
    report_path = str(tmp_path / "latest.md")
    write_markdown_report(summary, report_path)
    assert os.path.exists(report_path)
    content = Path(report_path).read_text()
    assert "invoice_extractor" in content
    assert "PASS" in content
    assert "FAIL" in content
