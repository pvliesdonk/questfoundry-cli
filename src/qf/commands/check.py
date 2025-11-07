"""Quality check and gatecheck commands"""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from qf.commands.validate import (
    SchemaNotFoundError,
    SchemaValidationError,
    validate_artifact_data,
)
from qf.utils import find_project_file

app = typer.Typer(help="Run quality checks and gatechecks")
console = Console()
logger = logging.getLogger(__name__)


@dataclass
class ArtifactData:
    """Parsed artifact file data"""

    path: Path
    data: dict[str, Any] | None
    error: str | None


def load_all_artifacts(workspace: Path) -> list[ArtifactData]:
    """
    Load all JSON files in workspace in a single pass.

    This consolidates file system operations to improve performance
    and allows individual checks to be self-contained.

    Args:
        workspace: Path to .questfoundry workspace

    Returns:
        List of ArtifactData objects, including files with errors
    """
    artifacts: list[ArtifactData] = []
    hot_path = workspace / "hot"

    if not hot_path.exists():
        return artifacts

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    artifacts.append(
                        ArtifactData(path=json_file, data=data, error=None)
                    )
                except json.JSONDecodeError as e:
                    logger.warning("Malformed JSON in %s: %s", json_file, str(e))
                    artifacts.append(
                        ArtifactData(
                            path=json_file,
                            data=None,
                            error=f"Invalid JSON: {str(e)}",
                        )
                    )
                except OSError as e:
                    logger.warning("Error reading %s: %s", json_file, str(e))
                    artifacts.append(
                        ArtifactData(
                            path=json_file,
                            data=None,
                            error=f"Could not read file: {str(e)}",
                        )
                    )

    return artifacts


def check_json_validity(artifacts: list[ArtifactData]) -> tuple[bool, list[str]]:
    """
    Check that all JSON files are valid and parseable.

    This check is self-contained and reports all file reading errors.
    """
    errors = []

    for artifact in artifacts:
        if artifact.error:
            errors.append(f"{artifact.path.name}: {artifact.error}")

    return len(errors) == 0, errors


def check_schema_conformance(artifacts: list[ArtifactData]) -> tuple[bool, list[str]]:
    """
    Check that all artifacts conform to their schemas.

    This check is self-contained and reports all schema validation errors.
    """
    errors = []

    for artifact in artifacts:
        # skip files with parse errors (handled by integrity check)
        if artifact.data is None:
            continue

        # get artifact type
        artifact_type = artifact.data.get("type")
        if not artifact_type:
            # this will be caught by required fields check
            continue

        # validate against schema
        try:
            is_valid, validation_errors = validate_artifact_data(
                artifact.data, artifact_type
            )
            if not is_valid:
                errors.append(
                    f"{artifact.path.name}: "
                    f"{len(validation_errors)} validation error(s)"
                )
        except SchemaNotFoundError:
            # schema doesn't exist - that's OK, skip validation
            logger.debug(
                "Schema %s not found for %s, skipping", artifact_type, artifact.path
            )
        except SchemaValidationError as e:
            # schema file itself is invalid
            logger.warning("Invalid schema %s: %s", artifact_type, str(e))
            errors.append(f"{artifact.path.name}: Schema error ({str(e)})")

    return len(errors) == 0, errors


def check_required_fields(artifacts: list[ArtifactData]) -> tuple[bool, list[str]]:
    """
    Check that artifacts have required common fields.

    This check is self-contained and reports all missing required fields.
    """
    errors = []
    required_fields = ["id", "type"]

    for artifact in artifacts:
        # skip files with parse errors (handled by integrity check)
        if artifact.data is None:
            continue

        for field in required_fields:
            if field not in artifact.data:
                errors.append(f"{artifact.path.name}: Missing '{field}' field")

    return len(errors) == 0, errors


def check_naming_conventions(artifacts: list[ArtifactData]) -> tuple[bool, list[str]]:
    """
    Check that files follow naming conventions.

    This check is self-contained and reports all naming violations.
    """
    errors = []

    for artifact in artifacts:
        # skip files with parse errors (handled by integrity check)
        if artifact.data is None:
            continue

        artifact_id = artifact.data.get("id")
        if artifact_id and f"{artifact_id}.json" != artifact.path.name:
            errors.append(
                f"{artifact.path.name}: Filename doesn't match "
                f"artifact ID '{artifact_id}'"
            )

    return len(errors) == 0, errors


@dataclass
class QualityBar:
    """Quality bar definition"""

    id: str
    name: str
    description: str
    check: Callable[[list[ArtifactData]], tuple[bool, list[str]]]


# Quality bar definitions
QUALITY_BARS: dict[str, QualityBar] = {
    "integrity": QualityBar(
        id="integrity",
        name="Integrity",
        description="All JSON files are valid and parseable",
        check=check_json_validity,
    ),
    "schema": QualityBar(
        id="schema",
        name="Schema Conformance",
        description="All artifacts conform to their schemas",
        check=check_schema_conformance,
    ),
    "required": QualityBar(
        id="required",
        name="Required Fields",
        description="All artifacts have required common fields",
        check=check_required_fields,
    ),
    "naming": QualityBar(
        id="naming",
        name="Naming Conventions",
        description="Files follow naming conventions",
        check=check_naming_conventions,
    ),
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

    # Load all artifacts once
    console.print("\n[bold cyan]Running Quality Checks[/bold cyan]\n")
    artifacts = load_all_artifacts(workspace)

    # Run checks
    results: dict[str, tuple[bool, list[str]]] = {}
    for bar_id in bars_to_run:
        bar = QUALITY_BARS[bar_id]
        console.print(f"Running {bar.name}...")
        passed, errors = bar.check(artifacts)
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
        passed, errors = results[bar_id]

        if passed:
            status = "[green]✓ PASS[/green]"
            issues = "0"
        else:
            status = "[red]✗ FAIL[/red]"
            issues = str(len(errors))
            all_passed = False

        table.add_row(bar.name, status, issues)

    console.print(table)

    # Show detailed errors if verbose
    if verbose and not all_passed:
        console.print("\n[bold]Detailed Errors:[/bold]\n")
        for bar_id in bars_to_run:
            passed, errors = results[bar_id]
            if not passed:
                bar = QUALITY_BARS[bar_id]
                console.print(f"[cyan]{bar.name}:[/cyan]")
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
