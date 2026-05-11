import os
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.text import Text

from pct.loader import load_suite
from pct.runner import run_suite
from pct.report import write_markdown_report

app = typer.Typer(help="prompt-contract-tester: test LLM prompts against YAML contracts")
console = Console()

REPORT_PATH = "reports/latest.md"

SAMPLE_YAML = """\
suite: {name}
prompt: |
  You are a helpful assistant. Return only valid JSON.

cases:
  - name: basic happy path
    input: |
      Sample input text here.
    mock_response: |
      {{"result": "ok", "confidence": 0.95}}
    expect:
      valid_json: true
      required_keys:
        - result
        - confidence
      assertions:
        - path: result
          equals: ok
        - path: confidence
          type: number
"""


@app.command()
def init(suite_name: str = typer.Argument(..., help="Name for the new test suite")):
    """Create a sample YAML test suite at tests/<suite_name>.yaml."""
    os.makedirs("tests", exist_ok=True)
    dest = Path("tests") / f"{suite_name}.yaml"
    if dest.exists():
        console.print(f"[yellow]File already exists:[/yellow] {dest}")
        raise typer.Exit(1)
    dest.write_text(SAMPLE_YAML.format(name=suite_name))
    console.print(f"[green]Created:[/green] {dest}")


@app.command()
def show(yaml_file: str = typer.Argument(..., help="Path to YAML test suite")):
    """Print suite name, prompt preview, and case names."""
    try:
        suite = load_suite(yaml_file)
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"[bold]Suite:[/bold] {suite['suite']}")
    prompt_preview = suite["prompt"].strip().replace("\n", " ")[:120]
    console.print(f"[bold]Prompt:[/bold] {prompt_preview}...")
    console.print(f"[bold]Cases ({len(suite['cases'])}):[/bold]")
    for i, case in enumerate(suite["cases"], 1):
        console.print(f"  {i}. {case.get('name', '(unnamed)')}")


@app.command()
def run(
    yaml_file: str = typer.Argument(..., help="Path to YAML test suite"),
    mock: bool = typer.Option(False, "--mock", help="Use mock responses (no API call)"),
):
    """Run a test suite and report pass/fail per case."""
    if not mock:
        console.print(
            "[red]Error:[/red] Live LLM calls aren't wired up yet. Use --mock to run against mock responses."
        )
        raise typer.Exit(1)

    try:
        suite = load_suite(yaml_file)
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"\n[bold]Running suite:[/bold] {suite['suite']}\n")
    summary = run_suite(suite, mock=mock)

    for case in summary["cases"]:
        if case["passed"]:
            label = Text("  PASS  ", style="bold white on green")
        else:
            label = Text("  FAIL  ", style="bold white on red")
        console.print(label, Text(f" {case['name']}"))
        for err in case["errors"]:
            console.print(f"         [dim]→ {err}[/dim]")

    console.print()
    console.print(
        f"[bold]Results:[/bold] {summary['passed']}/{summary['total']} passed"
        + (f"  [red]({summary['failed']} failed)[/red]" if summary["failed"] else "  [green](all passed)[/green]")
    )

    write_markdown_report(summary, REPORT_PATH)
    console.print(f"[dim]Report written to {REPORT_PATH}[/dim]")

    if summary["failed"] > 0:
        raise typer.Exit(1)


@app.command()
def report():
    """Print the latest report from reports/latest.md."""
    if not os.path.exists(REPORT_PATH):
        console.print(f"[red]No report found.[/red] Run 'pct run <file> --mock' first.")
        raise typer.Exit(1)
    with open(REPORT_PATH) as f:
        console.print(f.read())
