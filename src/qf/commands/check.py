"""Quality check and gatecheck commands"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from qf.commands.validate import validate_artifact_data
from qf.utils import find_project_file

app = typer.Typer(help="Run quality checks and gatechecks")
console = Console()


def check_json_validity(workspace: Path) -> tuple[bool, list[str]]:
    """Check that all JSON files in workspace are valid"""
    errors = []
    hot_path = workspace / "hot"

    if not hot_path.exists():
        return True, []

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    errors.append(f"{json_file.name}: {str(e)}")
                except OSError as e:
                    errors.append(f"{json_file.name}: Could not read file ({e})")

    return len(errors) == 0, errors


def check_schema_conformance(workspace: Path) -> tuple[bool, list[str]]:
    """Check that all artifacts conform to their schemas"""
    errors = []
    hot_path = workspace / "hot"

    if not hot_path.exists():
        return True, []

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)

                    # Get artifact type
                    artifact_type = data.get("type")
                    if not artifact_type:
                        errors.append(f"{json_file.name}: No 'type' field")
                        continue

                    # Validate against schema
                    try:
                        is_valid, validation_errors = validate_artifact_data(
                            data, artifact_type
                        )
                        if not is_valid:
                            errors.append(
                                f"{json_file.name}: "
                                f"{len(validation_errors)} validation error(s)"
                            )
                    except (FileNotFoundError, typer.Exit):
                        # Schema doesn't exist - that's OK, skip validation
                        pass

                except (json.JSONDecodeError, OSError):
                    # Already caught by JSON validity check
                    pass

    return len(errors) == 0, errors


def check_required_fields(workspace: Path) -> tuple[bool, list[str]]:
    """Check that artifacts have required common fields"""
    errors = []
    hot_path = workspace / "hot"

    if not hot_path.exists():
        return True, []

    required_fields = ["id", "type"]

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)

                    for field in required_fields:
                        if field not in data:
                            errors.append(f"{json_file.name}: Missing '{field}' field")

                except (json.JSONDecodeError, OSError):
                    # Already caught by other checks
                    pass

    return len(errors) == 0, errors


def check_naming_conventions(workspace: Path) -> tuple[bool, list[str]]:
    """Check that files follow naming conventions"""
    errors = []
    hot_path = workspace / "hot"

    if not hot_path.exists():
        return True, []

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            for json_file in artifact_dir.glob("*.json"):
                # Check that filename matches artifact ID
                try:
                    with open(json_file) as f:
                        data = json.load(f)

                    artifact_id = data.get("id")
                    if artifact_id and f"{artifact_id}.json" != json_file.name:
                        errors.append(
                            f"{json_file.name}: Filename doesn't match "
                            f"artifact ID '{artifact_id}'"
                        )

                except (json.JSONDecodeError, OSError):
                    # Already caught by other checks
                    pass

    return len(errors) == 0, errors


# Quality bar definitions
QUALITY_BARS: dict[str, dict[str, str | Callable[[Path], tuple[bool, list[str]]]]] = {
    "integrity": {
        "name": "Integrity",
        "description": "All JSON files are valid and parseable",
        "check": check_json_validity,
    },
    "schema": {
        "name": "Schema Conformance",
        "description": "All artifacts conform to their schemas",
        "check": check_schema_conformance,
    },
    "required": {
        "name": "Required Fields",
        "description": "All artifacts have required common fields",
        "check": check_required_fields,
    },
    "naming": {
        "name": "Naming Conventions",
        "description": "Files follow naming conventions",
        "check": check_naming_conventions,
    },
}


@app.command()
def run(
    bars: str | None = typer.Option(
        None,
        "--bars",
        "-b",
        help="Comma-separated list of bars to run (all by default)",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed error messages"
    ),
) -> None:
    """Run quality checks on the project"""
    # Check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    workspace = Path(".questfoundry")
    if not workspace.exists():
        console.print("[red]Error: Workspace not found[/red]")
        raise typer.Exit(1)

    # Determine which bars to run
    if bars:
        bars_to_run = [b.strip() for b in bars.split(",")]
        # Validate bar names
        invalid_bars = [b for b in bars_to_run if b not in QUALITY_BARS]
        if invalid_bars:
            console.print(f"[red]Invalid quality bars: {', '.join(invalid_bars)}[/red]")
            console.print(
                f"\n[cyan]Available bars:[/cyan] "
                f"{', '.join(QUALITY_BARS.keys())}"
            )
            raise typer.Exit(1)
    else:
        bars_to_run = list(QUALITY_BARS.keys())

    # Run checks
    console.print("\n[bold cyan]Running Quality Checks[/bold cyan]\n")

    results: dict[str, tuple[bool, list[str]]] = {}
    for bar_id in bars_to_run:
        bar = QUALITY_BARS[bar_id]
        bar_name = cast(str, bar["name"])
        bar_check = cast(Callable[[Path], tuple[bool, list[str]]], bar["check"])
        console.print(f"Running {bar_name}...")
        passed, errors = bar_check(workspace)
        results[bar_id] = (passed, errors)

    # Display results
    console.print("\n[bold]Quality Check Results[/bold]\n")

    table = Table(show_header=True)
    table.add_column("Quality Bar", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Issues", style="yellow")

    all_passed = True
    for bar_id in bars_to_run:
        bar = QUALITY_BARS[bar_id]
        bar_name = cast(str, bar["name"])
        passed, errors = results[bar_id]

        if passed:
            status = "[green]✓ PASS[/green]"
            issues = "0"
        else:
            status = "[red]✗ FAIL[/red]"
            issues = str(len(errors))
            all_passed = False

        table.add_row(bar_name, status, issues)

    console.print(table)

    # Show detailed errors if verbose
    if verbose and not all_passed:
        console.print("\n[bold]Detailed Errors:[/bold]\n")
        for bar_id in bars_to_run:
            passed, errors = results[bar_id]
            if not passed:
                bar = QUALITY_BARS[bar_id]
                bar_name = cast(str, bar["name"])
                console.print(f"[cyan]{bar_name}:[/cyan]")
                for error in errors:
                    console.print(f"  • {error}")
                console.print()

    # Summary
    console.print()
    if all_passed:
        console.print(
            Panel(
                f"[green]✓ All {len(bars_to_run)} quality checks passed[/green]",
                border_style="green",
            )
        )
    else:
        failed_count = sum(1 for _, (passed, _) in results.items() if not passed)
        console.print(
            Panel(
                f"[red]✗ {failed_count}/{len(bars_to_run)} quality checks failed[/red]",
                border_style="red",
            )
        )
        console.print(
            "\n[cyan]Tip:[/cyan] Use [green]--verbose[/green] "
            "to see detailed error messages\n"
        )

    # Note about future features
    console.print(
        "[dim]Note: Additional quality bars (style, consistency, completeness, etc.) "
        "will be available once Layer 6 integration is complete.[/dim]\n"
    )

    if not all_passed:
        raise typer.Exit(1)
