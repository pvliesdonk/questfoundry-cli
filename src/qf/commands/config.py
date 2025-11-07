"""Configuration management commands"""

from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.tree import Tree

from qf.utils import find_project_file

console = Console()
app = typer.Typer(help="Manage project configuration")


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
        with open(config_path) as f:
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
        with open(config_path, "w") as f:
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


def set_nested_value(config: dict[str, Any], key_path: str, value: str) -> None:
    """Set a nested value in config using dot notation"""
    keys = key_path.split(".")
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
