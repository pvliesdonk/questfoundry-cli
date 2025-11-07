"""Validation commands"""

import json
from pathlib import Path
from typing import Any

import jsonschema
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from qf.utils import find_project_file

app = typer.Typer(help="Validate artifacts and envelopes")
console = Console()


def get_schema_path(schema_name: str) -> Path:
    """Get path to a schema file"""
    # First, try spec submodule
    spec_path = Path(__file__).parent.parent.parent.parent / "spec" / "03-schemas"
    schema_file = spec_path / f"{schema_name}.schema.json"

    if schema_file.exists():
        return schema_file

    # If not found, raise error
    raise FileNotFoundError(f"Schema not found: {schema_name}")


def load_schema(schema_name: str) -> dict[str, Any]:
    """Load a JSON schema"""
    schema_path = get_schema_path(schema_name)

    try:
        with open(schema_path) as f:
            schema = json.load(f)
            if not isinstance(schema, dict):
                console.print(
                    f"[red]Error: Schema {schema_name} is not a valid object[/red]"
                )
                raise typer.Exit(1)
            return schema
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in schema {schema_name}: {e}[/red]")
        raise typer.Exit(1)
    except OSError as e:
        console.print(f"[red]Error reading schema {schema_name}: {e}[/red]")
        raise typer.Exit(1)


def validate_artifact_data(
    data: dict[str, Any], schema_name: str
) -> tuple[bool, list[str]]:
    """
    Validate artifact data against a schema.
    Returns (is_valid, errors) tuple.
    """
    try:
        schema = load_schema(schema_name)
        validator = jsonschema.Draft7Validator(schema)
        errors = []

        for error in validator.iter_errors(data):
            # Format error message with path
            path = ".".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{path}: {error.message}")

        return len(errors) == 0, errors

    except FileNotFoundError:
        console.print(f"[red]Schema not found: {schema_name}[/red]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf schema list[/green] "
            "to see available schemas"
        )
        raise typer.Exit(1)


def find_artifact_file(artifact_id: str) -> Path | None:
    """Find artifact file by ID in workspace"""
    workspace = Path(".questfoundry")
    if not workspace.exists():
        return None

    # Search in all hot workspace subdirectories
    hot_path = workspace / "hot"
    if not hot_path.exists():
        return None

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            # Try exact match
            artifact_file = artifact_dir / f"{artifact_id}.json"
            if artifact_file.exists():
                return artifact_file

            # Try matching by ID in file content
            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    if data.get("id") == artifact_id:
                        return json_file
                except (json.JSONDecodeError, KeyError, OSError):
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

    is_valid, errors = validate_artifact_data(data, schema)

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

    is_valid, errors = validate_artifact_data(data, schema)

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
