"""Validation commands"""

import json
import logging
from pathlib import Path
from typing import Any

import jsonschema
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from qf.commands.schema import get_schemas_path
from qf.utils import find_project_file

app = typer.Typer(help="Validate artifacts and envelopes")
console = Console()
logger = logging.getLogger(__name__)


class SchemaNotFoundError(Exception):
    """Raised when a schema file cannot be found"""

    pass


class SchemaValidationError(Exception):
    """Raised when schema file is invalid"""

    pass


def load_schema(schema_name: str) -> dict[str, Any]:
    """
    Load a JSON schema.

    Args:
        schema_name: Name of the schema (without .schema.json extension)

    Returns:
        Schema dictionary

    Raises:
        SchemaNotFoundError: If schema file doesn't exist
        SchemaValidationError: If schema file is invalid JSON or not a dict
    """
    try:
        schemas_path = get_schemas_path()
    except FileNotFoundError as e:
        raise SchemaNotFoundError(f"Schema directory not found: {e}") from e

    schema_file = schemas_path / f"{schema_name}.schema.json"

    if not schema_file.exists():
        raise SchemaNotFoundError(f"Schema not found: {schema_name}")

    try:
        with open(schema_file) as f:
            schema = json.load(f)
            if not isinstance(schema, dict):
                raise SchemaValidationError(
                    f"Schema {schema_name} is not a valid object"
                )
            return schema
    except json.JSONDecodeError as e:
        raise SchemaValidationError(
            f"Invalid JSON in schema {schema_name}: {e}"
        ) from e
    except OSError as e:
        raise SchemaValidationError(f"Error reading schema {schema_name}: {e}") from e


def validate_artifact_data(
    data: dict[str, Any], schema_name: str
) -> tuple[bool, list[str]]:
    """
    Validate artifact data against a schema.

    This is a pure function that performs validation without side effects.

    Args:
        data: Artifact data to validate
        schema_name: Name of the schema to validate against

    Returns:
        Tuple of (is_valid, errors) where errors is a list of error messages

    Raises:
        SchemaNotFoundError: If schema doesn't exist
        SchemaValidationError: If schema is invalid
    """
    schema = load_schema(schema_name)
    validator = jsonschema.Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(data):
        # format error message with path
        path = ".".join(str(p) for p in error.path) if error.path else "root"
        errors.append(f"{path}: {error.message}")

    return len(errors) == 0, errors


def find_artifact_file(artifact_id: str) -> Path | None:
    """
    Find artifact file by ID in workspace.

    Args:
        artifact_id: The artifact ID to search for

    Returns:
        Path to artifact file, or None if not found

    Note:
        Logs warnings for malformed JSON files encountered during search.
    """
    workspace = Path(".questfoundry")
    if not workspace.exists():
        return None

    # search in all hot workspace subdirectories
    hot_path = workspace / "hot"
    if not hot_path.exists():
        return None

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            # try exact match
            artifact_file = artifact_dir / f"{artifact_id}.json"
            if artifact_file.exists():
                return artifact_file

            # try matching by ID in file content
            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    if data.get("id") == artifact_id:
                        return json_file
                except json.JSONDecodeError as e:
                    logger.warning(
                        "Skipping malformed JSON file %s: %s", json_file, str(e)
                    )
                    continue
                except OSError as e:
                    logger.warning("Error reading file %s: %s", json_file, str(e))
                    continue
                except (KeyError, AttributeError):
                    # data.get() shouldn't raise these, but be defensive
                    continue

    return None


@app.command(name="artifact")
def validate_artifact(
    artifact_id: str = typer.Argument(..., help="Artifact ID to validate"),
    schema: str | None = typer.Option(
        None, "--schema", "-s", help="Schema name (auto-detected if not provided)"
    ),
) -> None:
    """Validate an artifact from the workspace"""
    # Check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Find artifact
    artifact_file = find_artifact_file(artifact_id)
    if not artifact_file:
        console.print(f"[red]Artifact not found: {artifact_id}[/red]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf list[/green] to see available artifacts"
        )
        raise typer.Exit(1)

    # Load artifact
    try:
        with open(artifact_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON in artifact file: {e}[/red]")
        raise typer.Exit(1)
    except OSError as e:
        console.print(f"[red]Error reading artifact: {e}[/red]")
        raise typer.Exit(1)

    # Determine schema
    if schema is None:
        # Auto-detect from artifact type
        artifact_type = data.get("type")
        if not artifact_type:
            console.print(
                "[red]Error: Artifact has no 'type' field and no schema specified[/red]"
            )
            console.print(
                "\n[cyan]Tip:[/cyan] Use [green]--schema <name>[/green] "
                "to specify schema explicitly"
            )
            raise typer.Exit(1)
        schema = artifact_type

    # Validate
    console.print(
        f"\nValidating [cyan]{artifact_id}[/cyan] "
        f"against schema [cyan]{schema}[/cyan]...\n"
    )

    try:
        is_valid, errors = validate_artifact_data(data, schema)
    except SchemaNotFoundError:
        console.print(f"[red]Schema not found: {schema}[/red]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf schema list[/green] "
            "to see available schemas"
        )
        raise typer.Exit(1)
    except SchemaValidationError as e:
        console.print(f"[red]Error loading schema: {e}[/red]")
        raise typer.Exit(1)

    if is_valid:
        console.print(Panel("[green]✓ Artifact is valid[/green]", border_style="green"))
    else:
        console.print(Panel("[red]✗ Validation failed[/red]", border_style="red"))

        # Display errors in table
        console.print("\n[bold]Validation Errors:[/bold]\n")
        error_table = Table(show_header=True)
        error_table.add_column("Field", style="cyan")
        error_table.add_column("Error", style="red")

        for error in errors:
            if ": " in error:
                field, message = error.split(": ", 1)
                error_table.add_row(field, message)
            else:
                error_table.add_row("", error)

        console.print(error_table)
        console.print()
        raise typer.Exit(1)


@app.command(name="file")
def validate_file(
    file_path: Path = typer.Argument(..., help="Path to JSON file"),
    schema: str = typer.Option(
        ..., "--schema", "-s", help="Schema name to validate against"
    ),
) -> None:
    """Validate a JSON file against a schema"""
    # Load file
    try:
        with open(file_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    except OSError as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        raise typer.Exit(1)

    # Validate
    console.print(
        f"\nValidating [cyan]{file_path.name}[/cyan] "
        f"against schema [cyan]{schema}[/cyan]...\n"
    )

    try:
        is_valid, errors = validate_artifact_data(data, schema)
    except SchemaNotFoundError:
        console.print(f"[red]Schema not found: {schema}[/red]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf schema list[/green] "
            "to see available schemas"
        )
        raise typer.Exit(1)
    except SchemaValidationError as e:
        console.print(f"[red]Error loading schema: {e}[/red]")
        raise typer.Exit(1)

    if is_valid:
        console.print(Panel("[green]✓ File is valid[/green]", border_style="green"))
    else:
        console.print(Panel("[red]✗ Validation failed[/red]", border_style="red"))

        # Display errors in table
        console.print("\n[bold]Validation Errors:[/bold]\n")
        error_table = Table(show_header=True)
        error_table.add_column("Field", style="cyan")
        error_table.add_column("Error", style="red")

        for error in errors:
            if ": " in error:
                field, message = error.split(": ", 1)
                error_table.add_row(field, message)
            else:
                error_table.add_row("", error)

        console.print(error_table)
        console.print()
        raise typer.Exit(1)


@app.command(name="envelope")
def validate_envelope(
    file_path: Path = typer.Argument(..., help="Envelope file path"),
) -> None:
    """Validate a Layer 4 envelope"""
    console.print("[yellow]Envelope validation coming soon[/yellow]")
    console.print(
        "[dim]Note: This will be implemented once Layer 4 envelope "
        "specifications are finalized.[/dim]"
    )
