"""Schema management commands"""

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Schema management")
console = Console()


def get_schemas_path() -> Path:
    """Get path to schemas directory"""
    # Look for spec submodule first
    spec_schemas = Path(__file__).parent.parent.parent.parent / "spec" / "03-schemas"
    if spec_schemas.exists():
        return spec_schemas

    # Fallback to installed package (future)
    try:
        import questfoundry

        pkg_path = Path(questfoundry.__file__).parent
        pkg_schemas = pkg_path / "resources" / "schemas"
        if pkg_schemas.exists():
            return pkg_schemas
    except ImportError:
        pass

    raise FileNotFoundError("Schema directory not found")


def list_schemas() -> list[str]:
    """List available schema files"""
    try:
        schemas_path = get_schemas_path()
        return [f.stem for f in schemas_path.glob("*.schema.json")]
    except FileNotFoundError:
        return []


def get_schema(name: str) -> Any:
    """Get schema by name"""
    schemas_path = get_schemas_path()
    schema_file = schemas_path / f"{name}.schema.json"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema not found: {name}")

    with open(schema_file) as f:
        return json.load(f)


@app.command("list")  # Use explicit name to avoid builtin shadowing
def list_() -> None:
    """List available schemas"""
    schemas = list_schemas()
    if not schemas:
        console.print(
            "[yellow]No schemas found. Is the spec submodule initialized?[/yellow]"
        )
        raise typer.Exit(1)

    table = Table(title="Available Schemas")
    table.add_column("Schema Name", style="cyan")
    table.add_column("Type", style="magenta")

    schema_name: str
    for schema_name in sorted(schemas):
        try:
            schema = get_schema(schema_name)
            schema_type: str = schema.get("type", "unknown")
            table.add_row(schema_name, schema_type)
        except Exception:
            table.add_row(schema_name, "error")

    console.print(table)


@app.command()
def show(name: str = typer.Argument(..., help="Schema name")) -> None:
    """Show schema details"""
    try:
        schema = get_schema(name)
        console.print_json(data=schema)
    except FileNotFoundError:
        console.print(f"[red]Schema not found: {name}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(name: str = typer.Argument(..., help="Schema name")) -> None:
    """Validate a schema file"""
    try:
        from questfoundry.validators import (  # type: ignore
            validate_schema as qf_validate_schema,
        )

        is_valid = qf_validate_schema(name)
        if is_valid:
            console.print(f"[green]✓ Schema is valid: {name}[/green]")
        else:
            console.print(f"[red]✗ Schema is invalid: {name}[/red]")
            raise typer.Exit(1)
    except ImportError:
        console.print(
            "[yellow]Schema validation not yet implemented in questfoundry-py[/yellow]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
