def get_response(
    prompt: str,
    user_input: str,
    mock_response: str = "",
    mock: bool = True,
) -> str:
    if mock:
        return mock_response or ""
    raise SystemExit(
        "Live LLM calls are not wired up yet. Run with --mock to use mock responses."
    )
