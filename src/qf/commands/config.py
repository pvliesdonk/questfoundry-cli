"""Configuration management commands"""

import os
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.tree import Tree

from qf.utils import find_project_file

console = Console()
app = typer.Typer(
    help="Manage project configuration",
    invoke_without_command=True,
)


def get_config_path() -> Path:
    """Get path to config file"""
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    config_path = Path(".questfoundry") / "config.yml"
    if not config_path.exists():
        console.print("[red]Error: Config file not found[/red]")
        console.print(
            "[cyan]Tip:[/cyan] The project may need to be re-initialized"
        )
        raise typer.Exit(1)

    return config_path


def load_config() -> dict[str, Any]:
    """Load configuration from YAML file"""
    config_path = get_config_path()
    try:
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        console.print(f"[red]Error parsing config file: {e}[/red]")
        raise typer.Exit(1)
    except (OSError, PermissionError) as e:
        console.print(f"[red]Error reading config file: {e}[/red]")
        raise typer.Exit(1)


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to YAML file"""
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
    except (OSError, PermissionError) as e:
        console.print(f"[red]Error writing config file: {e}[/red]")
        raise typer.Exit(1)


def is_sensitive(key: str) -> bool:
    """Check if a key contains sensitive information"""
    sensitive_terms = ["key", "secret", "token", "password", "api_key"]
    key_lower = key.lower()
    return any(term in key_lower for term in sensitive_terms)


def mask_value(value: Any, key: str) -> str:
    """Mask sensitive values"""
    if is_sensitive(key):
        if isinstance(value, str) and len(value) > 2:
            return f"{value[:2]}{'*' * 8}"
        return "********"
    return str(value)


def get_nested_value(config: dict[str, Any], key_path: str) -> tuple[Any, bool]:
    """
    Get a nested value from config using dot notation.
    Returns (value, found) tuple.
    """
    keys = key_path.split(".")
    current = config

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None, False
        current = current[key]

    return current, True


def normalize_provider_key(config: dict[str, Any], keys: list[str]) -> list[str]:
    """
    Normalize keys for case-insensitive provider name matching.
    If we're in the providers section with a provider name, find the actual key.
    """
    if len(keys) < 3 or keys[0] != "providers":
        return keys

    # For paths like 'providers.text.OpenAI.api_key', normalize the provider name (keys[2])
    normalized = keys[:2]  # ['providers', 'text']

    # Get or create the section
    current = config
    for key in normalized:
        if key not in current:
            current[key] = {}
        current = current[key]

    # Find the actual provider name (case-insensitive)
    if isinstance(current, dict):
        provider_name = keys[2]
        # Look for a case-insensitive match
        matching_key = None
        for existing_key in current.keys():
            if existing_key.lower() == provider_name.lower():
                matching_key = existing_key
                break
        # Use the existing key if found, otherwise use the provided one
        normalized.append(matching_key or provider_name)
    else:
        normalized.append(keys[2])

    # Add remaining keys
    normalized.extend(keys[3:])
    return normalized


def set_nested_value(config: dict[str, Any], key_path: str, value: str) -> None:
    """Set a nested value in config using dot notation"""
    keys = key_path.split(".")
    keys = normalize_provider_key(config, keys)
    current = config

    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            path = '.'.join(keys[:-1])
            console.print(f"[red]Error: '{path}' is not a dictionary[/red]")
            raise typer.Exit(1)
        current = current[key]

    # Set the final value
    final_key = keys[-1]

    # Try to parse value as boolean, int, float, or keep as string
    if value.lower() in ("true", "false"):
        current[final_key] = value.lower() == "true"
    else:
        # Try to parse as integer
        try:
            current[final_key] = int(value)
            return
        except ValueError:
            pass

        # Try to parse as float
        try:
            current[final_key] = float(value)
            return
        except ValueError:
            pass

        # Keep as string
        current[final_key] = value


def print_config_tree(
    config: dict[str, Any],
    tree: Tree | None = None,
    parent_key: str = "",
) -> Tree:
    """Recursively print config as a tree"""
    if tree is None:
        tree = Tree("⚙️  Configuration")

    for key, value in config.items():
        full_key = f"{parent_key}.{key}" if parent_key else key

        if isinstance(value, dict):
            branch = tree.add(f"[cyan]{key}[/cyan]")
            print_config_tree(value, branch, full_key)
        else:
            masked_value = mask_value(value, full_key)
            if is_sensitive(full_key):
                tree.add(f"[cyan]{key}:[/cyan] [dim]{masked_value}[/dim]")
            else:
                tree.add(f"[cyan]{key}:[/cyan] {masked_value}")

    return tree


@app.command(name="list")
def list_config() -> None:
    """Show current configuration"""
    config = load_config()

    if not config:
        console.print("\n[yellow]Configuration is empty[/yellow]\n")
        return

    tree = print_config_tree(config)
    console.print()
    console.print(tree)
    console.print()


@app.command(name="get")
def get_config(
    key: str = typer.Argument(..., help="Configuration key (dot notation)")
) -> None:
    """Get a specific configuration value"""
    config = load_config()
    value, found = get_nested_value(config, key)

    if not found:
        console.print(f"[red]Error: Configuration key not found: {key}[/red]")
        raise typer.Exit(1)

    # Display the value
    console.print(f"\n[cyan]{key}:[/cyan] ", end="")

    if isinstance(value, dict):
        console.print()
        tree = Tree(f"[cyan]{key}[/cyan]")
        print_config_tree(value, tree, key)
        console.print(tree)
    else:
        masked_value = mask_value(value, key)
        console.print(masked_value)

    console.print()


@app.command(name="set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key (dot notation)"),
    value: str = typer.Argument(..., help="Configuration value"),
) -> None:
    """Set a configuration value"""
    config = load_config()

    # Set the value
    try:
        set_nested_value(config, key, value)
        save_config(config)
        msg = f"[green]✓[/green] Configuration updated: [cyan]{key}[/cyan]"
        console.print(f"\n{msg} = {value}\n")
    except typer.Exit:
        raise
    except (OSError, PermissionError, yaml.YAMLError) as e:
        # File I/O errors or YAML serialization errors
        console.print(f"[red]Error setting configuration: {e}[/red]")
        raise typer.Exit(1)


def get_auto_configured_providers() -> dict[str, list[str]]:
    """Get providers that are auto-configured via environment variables"""
    auto_configured: dict[str, list[str]] = {}

    # Define provider environment variables
    env_vars = {
        "text": {
            "openai": ["OPENAI_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY"],
            "google": ["GOOGLE_API_KEY"],
            "cohere": ["COHERE_API_KEY"],
            "ollama": ["OLLAMA_BASE_URL"],
        },
        "image": {
            "stability": ["STABILITY_API_KEY"],
            "dalle": ["OPENAI_API_KEY"],
            "midjourney": ["MIDJOURNEY_API_KEY"],
            "a1111": ["A1111_BASE_URL"],
        },
    }

    for provider_type, providers in env_vars.items():
        for provider_id, env_var_list in providers.items():
            for env_var in env_var_list:
                if os.environ.get(env_var):
                    if provider_type not in auto_configured:
                        auto_configured[provider_type] = []
                    auto_configured[provider_type].append(provider_id)
                    break

    return auto_configured


@app.callback(invoke_without_command=True)
def config_callback(ctx: typer.Context) -> None:
    """Default behavior for config command - show configuration when no subcommand"""
    # If a subcommand was provided, don't do anything
    if ctx.invoked_subcommand is not None:
        return
    # Otherwise show the configuration (default to list)
    try:
        config = load_config()
        tree = Tree("⚙️  Configuration")

        if config:
            tree = print_config_tree(config, tree)

        # Add auto-configured providers section
        auto_configured = get_auto_configured_providers()
        if auto_configured:
            auto_tree = tree.add("[yellow]Auto-Configured Providers (from environment)[/yellow]")
            for provider_type in sorted(auto_configured.keys()):
                type_branch = auto_tree.add(f"[cyan]{provider_type}[/cyan]")
                for provider_id in sorted(auto_configured[provider_type]):
                    type_branch.add(f"[green]✓[/green] {provider_id}")

        if not config and not auto_configured:
            console.print("\n[yellow]Configuration is empty[/yellow]\n")
            return

        console.print()
        console.print(tree)
        console.print()
    except typer.Exit:
        raise
