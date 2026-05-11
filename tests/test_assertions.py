import pytest
from pct.assertions import evaluate_response


def test_valid_json_passes():
    result = evaluate_response('{"key": "value"}', {"valid_json": True})
    assert result["passed"] is True
    assert result["errors"] == []


def test_invalid_json_fails():
    result = evaluate_response("not json at all", {"valid_json": True})
    assert result["passed"] is False
    assert any("not valid JSON" in e for e in result["errors"])


def test_required_key_present_passes():
    result = evaluate_response('{"name": "Alice"}', {"valid_json": True, "required_keys": ["name"]})
    assert result["passed"] is True


def test_required_key_missing_fails():
    result = evaluate_response('{"name": "Alice"}', {"valid_json": True, "required_keys": ["name", "age"]})
    assert result["passed"] is False
    assert any("age" in e for e in result["errors"])


def test_forbidden_key_absent_passes():
    result = evaluate_response('{"name": "Alice"}', {"valid_json": True, "forbidden_keys": ["secret"]})
    assert result["passed"] is True


def test_forbidden_key_present_fails():
    result = evaluate_response('{"name": "Alice", "secret": "123"}', {"valid_json": True, "forbidden_keys": ["secret"]})
    assert result["passed"] is False
    assert any("secret" in e for e in result["errors"])


def test_equals_assertion_passes():
    result = evaluate_response(
        '{"status": "ok"}',
        {"valid_json": True, "assertions": [{"path": "status", "equals": "ok"}]},
    )
    assert result["passed"] is True


def test_equals_assertion_fails():
    result = evaluate_response(
        '{"status": "error"}',
        {"valid_json": True, "assertions": [{"path": "status", "equals": "ok"}]},
    )
    assert result["passed"] is False
    assert any("status" in e for e in result["errors"])


def test_type_number_passes():
    result = evaluate_response(
        '{"amount": 99.5}',
        {"valid_json": True, "assertions": [{"path": "amount", "type": "number"}]},
    )
    assert result["passed"] is True


def test_type_string_on_number_fails():
    result = evaluate_response(
        '{"amount": 99}',
        {"valid_json": True, "assertions": [{"path": "amount", "type": "string"}]},
    )
    assert result["passed"] is False


def test_type_boolean_passes():
    result = evaluate_response(
        '{"approved": true}',
        {"valid_json": True, "assertions": [{"path": "approved", "type": "boolean"}]},
    )
    assert result["passed"] is True


def test_contains_assertion_passes():
    result = evaluate_response(
        '{"message": "hello world"}',
        {"valid_json": True, "assertions": [{"path": "message", "contains": "hello"}]},
    )
    assert result["passed"] is True


def test_contains_assertion_fails():
    result = evaluate_response(
        '{"message": "goodbye"}',
        {"valid_json": True, "assertions": [{"path": "message", "contains": "hello"}]},
    )
    assert result["passed"] is False


def test_forbidden_values_passes():
    result = evaluate_response(
        '{"tool": "search_customer"}',
        {"valid_json": True, "forbidden_values": [{"path": "tool", "values": ["delete_customer"]}]},
    )
    assert result["passed"] is True


def test_forbidden_values_fails():
    result = evaluate_response(
        '{"tool": "delete_customer"}',
        {"valid_json": True, "forbidden_values": [{"path": "tool", "values": ["delete_customer"]}]},
    )
    assert result["passed"] is False
    assert any("delete_customer" in e for e in result["errors"])


def test_equals_boolean_cross_comparison():
    result = evaluate_response(
        '{"approved": true}',
        {"valid_json": True, "assertions": [{"path": "approved", "equals": True}]},
    )
    assert result["passed"] is True


def test_markdown_fenced_json_passes():
    response = '```json\n{"key": "value"}\n```'
    result = evaluate_response(response, {"valid_json": True, "required_keys": ["key"]})
    assert result["passed"] is True


def test_refusal_contains_passes():
    result = evaluate_response(
        "I cannot find the invoice. Missing data.",
        {"refusal_contains": ["missing", "invoice"]},
    )
    assert result["passed"] is True


def test_refusal_contains_fails():
    result = evaluate_response(
        "Here is your result.",
        {"refusal_contains": ["missing"]},
    )
    assert result["passed"] is False
