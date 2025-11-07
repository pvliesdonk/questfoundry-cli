"""Provider management commands"""

from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from qf.utils import find_project_file

from .config import load_config

console = Console()
app = typer.Typer(help="Manage AI providers")

# Known providers and their types
KNOWN_PROVIDERS = {
    "openai": {"type": "text", "name": "OpenAI"},
    "anthropic": {"type": "text", "name": "Anthropic"},
    "google": {"type": "text", "name": "Google (Gemini)"},
    "cohere": {"type": "text", "name": "Cohere"},
    "stability": {"type": "image", "name": "Stability AI"},
    "midjourney": {"type": "image", "name": "Midjourney"},
    "dalle": {"type": "image", "name": "DALL-E"},
}


def get_provider_status(provider_id: str, config: dict[str, Any]) -> str:
    """Check if provider is configured"""
    providers = config.get("providers", {})

    # Check text providers
    text_providers = providers.get("text", {})
    if provider_id in text_providers and isinstance(text_providers[provider_id], dict):
        return "configured"

    # Check image providers
    image_providers = providers.get("image", {})
    if provider_id in image_providers and isinstance(
        image_providers[provider_id], dict
    ):
        return "configured"

    return "not configured"


def get_default_provider(provider_type: str, config: dict[str, Any]) -> str | None:
    """Get the default provider for a given type"""
    providers = config.get("providers", {})
    type_config = providers.get(provider_type, {})
    return type_config.get("default") if isinstance(type_config, dict) else None


@app.command(name="list")
def list_providers() -> None:
    """List available AI providers"""
    # Check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Load config to check status
    config = load_config()

    # Get default providers
    default_text = get_default_provider("text", config)
    default_image = get_default_provider("image", config)

    # Create table
    table = Table(title="Available Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="white")
    table.add_column("Default", style="green")

    # Add text providers
    for provider_id, info in KNOWN_PROVIDERS.items():
        if info["type"] == "text":
            status = get_provider_status(provider_id, config)
            is_default = "✓" if provider_id == default_text else ""

            # Color status
            if status == "configured":
                status_display = "[green]✓ configured[/green]"
            else:
                status_display = "[dim]not configured[/dim]"

            table.add_row(
                info["name"],
                "text",
                status_display,
                is_default,
            )

    # Add image providers
    for provider_id, info in KNOWN_PROVIDERS.items():
        if info["type"] == "image":
            status = get_provider_status(provider_id, config)
            is_default = "✓" if provider_id == default_image else ""

            # Color status
            if status == "configured":
                status_display = "[green]✓ configured[/green]"
            else:
                status_display = "[dim]not configured[/dim]"

            table.add_row(
                info["name"],
                "image",
                status_display,
                is_default,
            )

    console.print()
    console.print(table)
    console.print()
    console.print(
        "[dim]Note: Provider integration will be fully available "
        "once Layer 6 is complete.[/dim]\n"
    )
    tip_msg = (
        "[cyan]Tip:[/cyan] Use [green]qf config set "
        "provider.text.<provider>.api_key <key>[/green] "
        "to configure a provider\n"
    )
    console.print(tip_msg)
