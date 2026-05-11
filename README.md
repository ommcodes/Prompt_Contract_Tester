# PCT — prompt_contract_tester

I write a lot of LLM-backed tools. And at some point I got tired of discovering that a prompt I tweaked last Tuesday broke something downstream — usually in production, usually on a Friday.

The problem isn't that models are bad at the task. The problem is that prompts have no tests. You change one sentence, you have no idea what you broke. You add a field to the expected output, nothing tells you it's missing. A key gets renamed in the response and your parser silently starts returning `None`. It's all vibes until something explodes.

`pct` is a small CLI tool I built to fix this for myself. You write test cases in YAML — here's the input, here's what the model should return, here's what should never appear — and it checks those rules against your mock responses. Fast, local, no API key needed.

It's not trying to be a full eval framework. It doesn't score outputs or run semantic comparisons. It catches the boring stuff that breaks 90% of real integrations: missing keys, wrong types, forbidden values, mangled JSON. The stuff that's embarrassing to have in production.

---

## Install

```bash
git clone https://github.com/YOUR_USERNAME/prompt-contract-tester
cd prompt-contract-tester
pip install -e .
```

Requires Python 3.10+.

---

## Quick start

```bash
# see what's in a test suite
pct show tests/invoice_extractor.yaml

# run it
pct run tests/invoice_extractor.yaml --mock

# print the last report
pct report

# scaffold a new suite
pct init my_extractor
```

---

## Writing a test suite

Everything lives in a YAML file. The format is intentionally simple:

```yaml
suite: invoice_extractor
prompt: |
  Extract invoice fields from the text below.
  Return only a JSON object with no extra commentary.

cases:
  - name: normal invoice
    input: |
      Invoice INV-1029 from Acme Supplies.
      Total due: USD 1248.50.
    mock_response: |
      {
        "invoice_number": "INV-1029",
        "vendor_name": "Acme Supplies",
        "total_amount": 1248.50,
        "currency": "USD"
      }
    expect:
      valid_json: true
      required_keys:
        - invoice_number
        - vendor_name
        - total_amount
        - currency
      assertions:
        - path: invoice_number
          equals: INV-1029
        - path: total_amount
          type: number
        - path: currency
          equals: USD
```

The `mock_response` is what you use while developing — paste in a real model output you got once and lock it in as your reference. When you change the prompt, you rerun the tests to see what broke.

---

## What you can assert

### JSON structure

```yaml
expect:
  valid_json: true
  required_keys:
    - invoice_number
    - vendor_name
  forbidden_keys:
    - internal_id
    - debug_info
```

### Value checks

```yaml
assertions:
  - path: status
    equals: approved

  - path: confidence
    type: number        # string | number | boolean

  - path: summary
    contains: invoice

  - path: customer.name   # dot paths work for nested fields
    type: string
```

### Blocking dangerous outputs

This is the one I use most for agent tool-call prompts:

```yaml
forbidden_values:
  - path: tool
    values:
      - delete_customer
      - drop_table
      - send_email
```

If the model's JSON has `"tool": "delete_customer"`, the test fails. Good for making sure your agent prompts don't hallucinate destructive actions.

### Refusal checks

```yaml
refusal_contains:
  - cannot
  - insufficient information
```

Useful when you want to verify the model says it can't do something, not that it tries anyway.

---

## Mock mode

All tests run against `mock_response` in your YAML file — no API calls, no keys, no network. This means:

- Tests run in under a second
- You can run them in CI with no credentials
- You can pin a specific response and test it stays valid across prompt changes

The typical workflow is: get a real response from the model once, paste it in as `mock_response`, write assertions for it, and then your test suite guards that contract from there on.

Live LLM calls aren't wired up yet. That's on the roadmap.

---

## Example output

```
Running suite: invoice_extractor

  PASS   normal invoice
  FAIL   missing required fields
         → required_keys: missing key 'total_amount'
         → required_keys: missing key 'currency'
  FAIL   forbidden key present
         → forbidden_keys: key 'vendor_id' must not be present

Results: 1/3 passed  (2 failed)
Report written to reports/latest.md
```

The process exits with code 1 if anything fails, so it drops straight into CI pipelines.

---

## Project layout

```
pct/
  cli.py          # typer commands: init, show, run, report
  loader.py       # loads and validates YAML suites
  assertions.py   # evaluates expect blocks against a response
  runner.py       # runs all cases in a suite
  json_utils.py   # json parsing, dot-path traversal, fence stripping
  report.py       # writes reports/latest.md
tests/
  invoice_extractor.yaml
  agent_tool_planner.yaml
  test_loader.py
  test_assertions.py
  test_runner.py
```

---

## Running the tests

```bash
pytest
```

All 32 tests use mock responses — no network, no keys.

---

## What it doesn't do (yet)

- Live model calls
- Array index paths (`items.0.name` — dot paths only for now)
- JSON Schema validation
- Scoring or fuzzy matching
- HTML reports
- Parallel case execution

Most of these aren't hard to add — the assertion evaluator is one function, easy to extend.

---

## Why not just use pytest directly?

You can, and sometimes that's the right call. But writing raw pytest for every prompt gets verbose fast, and it doesn't give non-engineers a way to read or write tests. YAML suites are easy to review in a PR, easy to hand to someone who doesn't write Python, and easy to version alongside the prompt they're testing.

It's a different tradeoff, not a better one in every case.

## License

This project is licensed under the **PolyForm Noncommercial License 1.0.0**.

You may use, modify, and distribute this software for **noncommercial purposes only** — including personal use, research, education, and use by nonprofit/government organisations. Commercial use of any kind is not permitted without explicit written permission from the author.

Full license text: [LICENSE](./LICENSE)
Canonical URL: https://polyformproject.org/licenses/noncommercial/1.0.0
