"""Validation commands"""

import typer
import json
from pathlib import Path
from rich.console import Console
from questfoundry import validate_instance_detailed

app = typer.Typer(help="Validate artifacts and envelopes")
console = Console()

@app.command()
def artifact(
    file: Path = typer.Argument(..., help="Artifact file path"),
    schema: str = typer.Option(..., "--schema", "-s", help="Schema name"),
):
    """Validate an artifact against a schema"""
    try:
        with open(file) as f:
            instance = json.load(f)

        result = validate_instance_detailed(instance, schema)

        if result["valid"]:
            console.print(f"[green]✓ Artifact is valid[/green]")
        else:
            console.print(f"[red]✗ Validation failed[/red]")
            for error in result["errors"]:
                console.print(f"  [red]- {error}[/red]")
            raise typer.Exit(1)

    except FileNotFoundError:
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def envelope(
    file: Path = typer.Argument(..., help="Envelope file path"),
):
    """Validate a Layer 4 envelope"""
    console.print("[yellow]Envelope validation coming soon[/yellow]")
    # Implementation will depend on Layer 4 envelope schema
    