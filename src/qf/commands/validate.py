"""Validation commands"""

import json
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Validate artifacts and envelopes")
console = Console()


@app.command()
def artifact(
    file: Path = typer.Argument(..., help="Artifact file path"),
    schema: str = typer.Option(..., "--schema", "-s", help="Schema name"),
) -> None:
    """Validate an artifact against a schema"""
    try:
        with open(file) as f:
            instance = json.load(f)

        try:
            from questfoundry import validate_instance

            is_valid = validate_instance(instance, schema)
            if is_valid:
                console.print("[green]✓ Artifact is valid[/green]")
            else:
                console.print("[red]✗ Validation failed[/red]")
                console.print(
                    "[yellow]Note: Detailed errors not yet available[/yellow]"
                )
                raise typer.Exit(1)
        except ImportError:
            console.print(
                "[yellow]Validation not yet fully implemented "
                "in questfoundry-py[/yellow]"
            )
            console.print(f"[cyan]Loaded artifact from {file}[/cyan]")
            console.print(f"[cyan]Target schema: {schema}[/cyan]")

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
) -> None:
    """Validate a Layer 4 envelope"""
    console.print("[yellow]Envelope validation coming soon[/yellow]")
    # Implementation will depend on Layer 4 envelope schema
