"""Schema management commands"""

import typer
from rich.console import Console
from rich.table import Table
from questfoundry import list_schemas, get_schema

app = typer.Typer(help="Schema management")
console = Console()

@app.command()
def list():
    """List available schemas"""
    schemas = list_schemas()
    table = Table(title="Available Schemas")
    table.add_column("Schema Name", style="cyan")
    table.add_column("Type", style="magenta")

    for schema_name in sorted(schemas):
        schema = get_schema(schema_name)
        schema_type = schema.get("type", "unknown")
        table.add_row(schema_name, schema_type)

    console.print(table)

@app.command()
def show(name: str = typer.Argument(..., help="Schema name")):
    """Show schema details"""
    try:
        schema = get_schema(name)
        console.print_json(data=schema)
    except FileNotFoundError:
        console.print(f"[red]Schema not found: {name}[/red]")
        raise typer.Exit(1)

@app.command()
def validate(name: str = typer.Argument(..., help="Schema name")):
    """Validate a schema file"""
    from questfoundry.validators import validate_schema
    try:
        is_valid = validate_schema(name)
        if is_valid:
            console.print(f"[green]✓ Schema is valid: {name}[/green]")
        else:
            console.print(f"[red]✗ Schema is invalid: {name}[/red]")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
        