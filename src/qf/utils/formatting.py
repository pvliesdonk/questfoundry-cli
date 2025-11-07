"""Rich console formatting utilities"""

from rich.console import Console

console = Console()


def print_header(text: str) -> None:
    """Print a formatted header"""
    console.print(f"\n[bold cyan]{text}[/bold cyan]\n")


def print_success(text: str) -> None:
    """Print a success message"""
    console.print(f"[green]✓ {text}[/green]")


def print_error(text: str) -> None:
    """Print an error message"""
    console.print(f"[red]✗ {text}[/red]")


def print_info(text: str) -> None:
    """Print an info message"""
    console.print(f"[blue]ℹ {text}[/blue]")


def print_warning(text: str) -> None:
    """Print a warning message"""
    console.print(f"[yellow]⚠ {text}[/yellow]")
