from pct.llm_client import get_response
from pct.assertions import evaluate_response


def run_suite(suite: dict, mock: bool = True) -> dict:
    results = []
    for case in suite["cases"]:
        response = get_response(
            prompt=suite["prompt"],
            user_input=case.get("input", ""),
            mock_response=case.get("mock_response", ""),
            mock=mock,
        )
        evaluation = evaluate_response(response, case.get("expect", {}))
        results.append(
            {
                "name": case.get("name", "(unnamed)"),
                "passed": evaluation["passed"],
                "errors": evaluation["errors"],
                "response_preview": response[:120] if response else "",
            }
        )

    passed = sum(1 for r in results if r["passed"])
    return {
        "suite": suite["suite"],
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "cases": results,
    }
