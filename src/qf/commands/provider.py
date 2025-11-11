"""Provider management commands"""

import os
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
    "openai": {"type": "text", "name": "OpenAI", "env_vars": ["OPENAI_API_KEY"]},
    "anthropic": {"type": "text", "name": "Anthropic", "env_vars": ["ANTHROPIC_API_KEY"]},
    "google": {"type": "text", "name": "Google (Gemini)", "env_vars": ["GOOGLE_API_KEY"]},
    "cohere": {"type": "text", "name": "Cohere", "env_vars": ["COHERE_API_KEY"]},
    "stability": {"type": "image", "name": "Stability AI", "env_vars": ["STABILITY_API_KEY"]},
    "midjourney": {"type": "image", "name": "Midjourney", "env_vars": ["MIDJOURNEY_API_KEY"]},
    "dalle": {"type": "image", "name": "DALL-E", "env_vars": ["OPENAI_API_KEY"]},
    "ollama": {"type": "text", "name": "Ollama (Local)", "env_vars": ["OLLAMA_BASE_URL"]},
    "a1111": {"type": "image", "name": "A1111 (Local)", "env_vars": ["A1111_BASE_URL"]},
}


def get_provider_status(provider_id: str, config: dict[str, Any]) -> str:
    """Check if provider is configured via config or environment variables"""
    providers = config.get("providers", {})

    # Check text providers in config
    text_providers = providers.get("text", {})
    if provider_id in text_providers and isinstance(text_providers[provider_id], dict):
        return "configured"

    # Check image providers in config
    image_providers = providers.get("image", {})
    if provider_id in image_providers and isinstance(
        image_providers[provider_id], dict
    ):
        return "configured"

    # Check environment variables
    if provider_id in KNOWN_PROVIDERS:
        env_vars = KNOWN_PROVIDERS[provider_id].get("env_vars", [])
        for env_var in env_vars:
            if os.environ.get(env_var):
                return "auto-configured"

    return "not configured"


def get_default_provider(provider_type: str, config: dict[str, Any]) -> str | None:
    """Get the default provider for a given type"""
    providers = config.get("providers", {})
    type_config = providers.get(provider_type, {})
    return type_config.get("default") if isinstance(type_config, dict) else None


def add_providers_to_table(
    table: Table,
    provider_type: str,
    config: dict[str, Any],
    default_provider: str | None,
) -> None:
    """Add providers of a specific type to the table"""
    for provider_id, info in KNOWN_PROVIDERS.items():
        if info["type"] == provider_type:
            status = get_provider_status(provider_id, config)
            is_default = "✓" if provider_id == default_provider else ""

            # Color status
            if status == "configured":
                status_display = "[green]✓ configured[/green]"
            elif status == "auto-configured":
                status_display = "[yellow]⚙ auto-configured[/yellow]"
            else:
                status_display = "[dim]not configured[/dim]"

            table.add_row(
                info["name"],
                provider_type,
                status_display,
                is_default,
            )


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

    # Add text and image providers
    add_providers_to_table(table, "text", config, default_text)
    add_providers_to_table(table, "image", config, default_image)

    console.print()
    console.print(table)
    console.print()
    console.print(
        "[dim]Note: Provider integration will be fully available "
        "once Layer 6 is complete.[/dim]\n"
    )
    tip_msg = (
        "[cyan]Tip:[/cyan] Use [green]qf config set "
        "providers.text.<provider>.api_key <key>[/green] "
        "to configure a provider\n"
    )
    console.print(tip_msg)
