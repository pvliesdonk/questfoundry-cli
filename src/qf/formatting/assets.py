"""Asset preview and formatting utilities"""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def format_image_info(image_path: str, width: int = 1024, height: int = 1024) -> Panel:
    """Format image asset information.

    Args:
        image_path: Path to the generated image
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Rich Panel with formatted image info
    """
    return Panel(
        f"[cyan]Path:[/cyan] {image_path}\n"
        f"[cyan]Dimensions:[/cyan] {width}x{height}\n"
        f"[cyan]Format:[/cyan] PNG",
        title="[bold green]Image Asset[/bold green]",
        border_style="green",
    )


def format_audio_info(
    audio_path: str, duration: str = "3:45", format_type: str = "MP3", bitrate: str = "192kbps"
) -> Panel:
    """Format audio asset information.

    Args:
        audio_path: Path to the generated audio file
        duration: Duration of audio (MM:SS or MM:SS format)
        format_type: Audio format (MP3, WAV, etc.)
        bitrate: Audio bitrate

    Returns:
        Rich Panel with formatted audio info
    """
    return Panel(
        f"[cyan]Path:[/cyan] {audio_path}\n"
        f"[cyan]Duration:[/cyan] {duration}\n"
        f"[cyan]Format:[/cyan] {format_type}\n"
        f"[cyan]Bitrate:[/cyan] {bitrate}",
        title="[bold green]Audio Asset[/bold green]",
        border_style="green",
    )


def display_prose_preview(prose: str, max_length: int = 500) -> None:
    """Display a preview of generated prose.

    Args:
        prose: The prose text to display
        max_length: Maximum length of preview (will truncate longer prose)
    """
    if len(prose) > max_length:
        preview = prose[:max_length] + "..."
    else:
        preview = prose

    console.print("\n[bold cyan]Scene Preview:[/bold cyan]\n")
    console.print(f"[dim]{preview}[/dim]\n")


def create_generation_summary_table(
    generations: list[dict[str, Any]],
) -> Table:
    """Create a Rich table summarizing batch generation results.

    Args:
        generations: List of generation result dicts with keys:
            - id: Artifact ID
            - type: Asset type (image, audio, etc.)
            - path: Path to generated asset
            - status: Status (success, failed, etc.)
            - duration: Generation time

    Returns:
        Rich Table with summary
    """
    table = Table(title="Generation Summary")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Path", style="blue")
    table.add_column("Duration", style="yellow")

    for gen in generations:
        status_display = (
            "[green]✓[/green]" if gen.get("status") == "success" else "[red]✗[/red]"
        )
        table.add_row(
            gen.get("id", ""),
            gen.get("type", ""),
            status_display,
            gen.get("path", ""),
            gen.get("duration", ""),
        )

    return table


def show_image_viewer_instructions(image_path: str) -> None:
    """Display instructions for viewing a generated image.

    Args:
        image_path: Path to the image file
    """
    console.print(
        Panel(
            f"To view the image, run:\n\n"
            f"[green]open {image_path}[/green] (macOS)\n"
            f"[green]xdg-open {image_path}[/green] (Linux)\n"
            f"[green]start {image_path}[/green] (Windows)\n",
            title="[bold cyan]View Image[/bold cyan]",
            border_style="cyan",
        )
    )


def show_audio_player_instructions(audio_path: str) -> None:
    """Display instructions for playing a generated audio file.

    Args:
        audio_path: Path to the audio file
    """
    console.print(
        Panel(
            f"To play the audio, run:\n\n"
            f"[green]afplay {audio_path}[/green] (macOS)\n"
            f"[green]play {audio_path}[/green] (Linux - SoX)\n"
            f"[green]powershell -Command (New-Object Media.SoundPlayer).PlaySync('{audio_path}')[/green] (Windows)\n",
            title="[bold cyan]Play Audio[/bold cyan]",
            border_style="cyan",
        )
    )


def create_asset_inventory_table(asset_types: dict[str, list[str]]) -> Table:
    """Create an inventory table of all generated assets.

    Args:
        asset_types: Dict mapping asset type to list of file paths
            Example: {"images": ["img1.png", "img2.png"], "audio": ["audio1.mp3"]}

    Returns:
        Rich Table with asset inventory
    """
    table = Table(title="Asset Inventory")
    table.add_column("Type", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Location", style="green")

    for asset_type, files in asset_types.items():
        table.add_row(
            asset_type.capitalize(),
            str(len(files)),
            f".questfoundry/assets/{asset_type.lower()}/",
        )

    return table
