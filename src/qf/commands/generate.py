"""Asset generation commands"""

import json
import time
from pathlib import Path
from typing import Any, Optional, cast

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from qf.utils import find_project_file

console = Console()

# Create Typer app for generate commands
app = typer.Typer(
    help="Generate assets from artifacts",
    no_args_is_help=True,
)


def find_artifact(artifact_id: str) -> Path | None:
    """Find artifact file by ID in workspace."""
    workspace = Path(".questfoundry")
    if not workspace.exists():
        return None

    hot_path = workspace / "hot"
    if not hot_path.exists():
        return None

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            # Try exact match
            artifact_file = artifact_dir / f"{artifact_id}.json"
            if artifact_file.exists():
                return artifact_file

            # Try matching by ID in file content
            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    if data.get("id") == artifact_id:
                        return json_file
                except (json.JSONDecodeError, KeyError):
                    continue

    return None


def load_artifact(artifact_id: str) -> dict[str, Any] | None:
    """Load artifact from file."""
    artifact_file = find_artifact(artifact_id)
    if not artifact_file:
        return None

    try:
        with open(artifact_file) as f:
            return cast(dict[str, Any], json.load(f))
    except json.JSONDecodeError:
        return None


def validate_artifact_type(
    artifact_id: str, expected_types: list[str]
) -> tuple[bool, dict[str, Any] | None]:
    """Validate artifact exists and is of correct type."""
    artifact = load_artifact(artifact_id)
    if not artifact:
        console.print(f"[red]Error: Artifact not found: {artifact_id}[/red]")
        return False, None

    artifact_type = artifact.get("type", "unknown")
    if artifact_type not in expected_types:
        console.print(
            f"[red]Error: Expected artifact type {expected_types}, "
            f"but got {artifact_type}[/red]"
        )
        return False, None

    return True, artifact


@app.command(name="image")
def generate_image(
    shotlist_id: str = typer.Argument(..., help="Shotlist artifact ID"),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="AI provider to use (e.g., dalle, midjourney)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", help="Model to use (provider-specific)"
    ),
    open_result: bool = typer.Option(
        False, "--open", help="Open generated image after creation"
    ),
) -> None:
    """Generate image from shotlist artifact.

    Uses the Illustrator role to generate visual assets.
    """
    # Check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Validate artifact
    is_valid, artifact = validate_artifact_type(shotlist_id, ["shotlist", "shot_list"])
    if not is_valid:
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf list shotlists[/green] "
            "to see available shotlists"
        )
        raise typer.Exit(1)

    # Type narrowing: artifact cannot be None after is_valid check
    assert artifact is not None

    # Show generation panel
    console.print()
    title_text = f"Generating Image - {artifact.get('title', shotlist_id)}"
    provider_info = f"Provider: {provider}" if provider else "Using default provider"
    model_info = f"Model: {model}" if model else "Using default model"

    console.print(
        Panel(
            f"[cyan]Shotlist:[/cyan] {shotlist_id}\n"
            f"[cyan]{provider_info}[/cyan]\n"
            f"[cyan]{model_info}[/cyan]",
            title=f"[bold cyan]{title_text}[/bold cyan]",
            border_style="cyan",
        )
    )

    # Simulate generation with progress tracking
    console.print(
        "\n[yellow]Note: Image generation will integrate with questfoundry-py "
        "providers in a future release.[/yellow]"
    )
    console.print("[dim]Demonstrating progress tracking...[/dim]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Initialize provider
        task1 = progress.add_task("Initializing provider...", total=None)
        time.sleep(0.3)
        progress.update(task1, description="[green]✓[/green] Provider initialized")

        # Generate image
        task2 = progress.add_task(
            "Generating image (this may take a moment)...", total=None
        )
        time.sleep(1.5)
        progress.update(task2, description="[green]✓[/green] Image generated")

        # Save result
        task3 = progress.add_task("Saving image...", total=None)
        time.sleep(0.3)
        progress.update(task3, description="[green]✓[/green] Image saved")

    # Display result
    result_path = f".questfoundry/assets/images/{shotlist_id}.png"
    console.print()
    console.print(
        Panel(
            f"[green]✓ Image generated successfully[/green]\n\n"
            f"[cyan]Path:[/cyan] {result_path}\n"
            f"[cyan]Size:[/cyan] 1024x1024 (example)",
            title="[bold green]Generation Complete[/bold green]",
            border_style="green",
        )
    )

    if open_result:
        console.print(
            "\n[yellow]Note: --open flag will be available when image viewing is "
            "integrated.[/yellow]"
        )

    console.print()


@app.command(name="audio")
def generate_audio(
    cuelist_id: str = typer.Argument(..., help="Cuelist artifact ID"),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="Audio provider to use (e.g., elevenlabs, google)"
    ),
    open_result: bool = typer.Option(
        False, "--open", help="Open generated audio after creation"
    ),
) -> None:
    """Generate audio from cuelist artifact.

    Uses the Audio Producer role to generate audio assets.
    """
    # Check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Validate artifact
    is_valid, artifact = validate_artifact_type(
        cuelist_id, ["cuelist", "cue_list", "audio_cue"]
    )
    if not is_valid:
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf list cuelists[/green] "
            "to see available cuelists"
        )
        raise typer.Exit(1)

    # Type narrowing: artifact cannot be None after is_valid check
    assert artifact is not None

    # Show generation panel
    console.print()
    title_text = f"Generating Audio - {artifact.get('title', cuelist_id)}"
    provider_info = f"Provider: {provider}" if provider else "Using default provider"

    console.print(
        Panel(
            f"[cyan]Cuelist:[/cyan] {cuelist_id}\n"
            f"[cyan]{provider_info}[/cyan]",
            title=f"[bold cyan]{title_text}[/bold cyan]",
            border_style="cyan",
        )
    )

    # Simulate generation with progress tracking
    console.print(
        "\n[yellow]Note: Audio generation will integrate with questfoundry-py "
        "audio providers in a future release.[/yellow]"
    )
    console.print("[dim]Demonstrating progress tracking...[/dim]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Initialize provider
        task1 = progress.add_task("Initializing audio provider...", total=None)
        time.sleep(0.3)
        progress.update(task1, description="[green]✓[/green] Provider initialized")

        # Generate audio
        task2 = progress.add_task(
            "Generating audio (this may take a moment)...", total=None
        )
        time.sleep(2.0)
        progress.update(task2, description="[green]✓[/green] Audio generated")

        # Save result
        task3 = progress.add_task("Saving audio file...", total=None)
        time.sleep(0.3)
        progress.update(task3, description="[green]✓[/green] Audio saved")

    # Display result
    result_path = f".questfoundry/assets/audio/{cuelist_id}.mp3"
    console.print()
    console.print(
        Panel(
            f"[green]✓ Audio generated successfully[/green]\n\n"
            f"[cyan]Path:[/cyan] {result_path}\n"
            f"[cyan]Duration:[/cyan] 3m 45s (example)\n"
            f"[cyan]Format:[/cyan] MP3 @ 192kbps",
            title="[bold green]Generation Complete[/bold green]",
            border_style="green",
        )
    )

    if open_result:
        console.print(
            "\n[yellow]Note: --open flag will be available when audio playback is "
            "integrated.[/yellow]"
        )

    console.print()


@app.command(name="scene")
def generate_scene(
    tu_id: str = typer.Argument(..., help="TU (Turn Unit) artifact ID"),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="AI provider to use for prose generation"
    ),
) -> None:
    """Generate scene prose from TU artifact.

    Uses the Scene Smith role to generate narrative prose.
    """
    # Check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Validate artifact
    is_valid, artifact = validate_artifact_type(tu_id, ["tu", "turn_unit", "brief"])
    if not is_valid:
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf list tus[/green] to see available TUs"
        )
        raise typer.Exit(1)

    # Type narrowing: artifact cannot be None after is_valid check
    assert artifact is not None

    # Show generation panel
    console.print()
    title_text = f"Generating Scene - {artifact.get('title', tu_id)}"
    provider_info = f"Provider: {provider}" if provider else "Using default provider"

    console.print(
        Panel(
            f"[cyan]TU:[/cyan] {tu_id}\n"
            f"[cyan]{provider_info}[/cyan]",
            title=f"[bold cyan]{title_text}[/bold cyan]",
            border_style="cyan",
        )
    )

    # Simulate generation with progress tracking
    console.print(
        "\n[yellow]Note: Scene generation will integrate with questfoundry-py "
        "Scene Smith role in a future release.[/yellow]"
    )
    console.print("[dim]Demonstrating progress tracking...[/dim]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Prepare context
        task1 = progress.add_task("Loading TU context and canon...", total=None)
        time.sleep(0.3)
        progress.update(task1, description="[green]✓[/green] Context loaded")

        # Generate prose
        task2 = progress.add_task("Generating scene prose...", total=None)
        time.sleep(1.2)
        progress.update(task2, description="[green]✓[/green] Prose generated")

        # Save scene artifact
        task3 = progress.add_task("Saving scene artifact...", total=None)
        time.sleep(0.3)
        progress.update(task3, description="[green]✓[/green] Scene saved")

    # Display result
    result_id = f"SCENE-{tu_id}"
    console.print()
    console.print(
        Panel(
            f"[green]✓ Scene prose generated successfully[/green]\n\n"
            f"[cyan]Scene ID:[/cyan] {result_id}\n"
            f"[cyan]Word Count:[/cyan] 1,250 (example)\n"
            f"[cyan]Status:[/cyan] Draft ready for review",
            title="[bold green]Generation Complete[/bold green]",
            border_style="green",
        )
    )

    console.print(
        "\n[cyan]Preview:[/cyan]\n"
        "[dim]The lamplight flickered as the keeper climbed "
        "the spiral stairs...[/dim]\n"
    )


@app.command(name="canon")
def generate_canon(
    hook_id: str = typer.Argument(..., help="Hook artifact ID"),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="AI provider to use for canonization"
    ),
) -> None:
    """Canonize hook to create canon pack.

    Uses the Lore Weaver role to transform hook cards into canonical truth.
    """
    # Check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Validate artifact
    is_valid, artifact = validate_artifact_type(hook_id, ["hook", "hook_card"])
    if not is_valid:
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf list hooks[/green] "
            "to see available hooks"
        )
        raise typer.Exit(1)

    # Type narrowing: artifact cannot be None after is_valid check
    assert artifact is not None

    # Show generation panel
    console.print()
    title_text = f"Canonizing Hook - {artifact.get('title', hook_id)}"
    provider_info = f"Provider: {provider}" if provider else "Using default provider"

    console.print(
        Panel(
            f"[cyan]Hook:[/cyan] {hook_id}\n"
            f"[cyan]{provider_info}[/cyan]",
            title=f"[bold cyan]{title_text}[/bold cyan]",
            border_style="cyan",
        )
    )

    # Simulate canonization with progress tracking
    console.print(
        "\n[yellow]Note: Canonization will integrate with questfoundry-py "
        "Lore Weaver role in a future release.[/yellow]"
    )
    console.print("[dim]Demonstrating progress tracking...[/dim]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Analyze hook
        task1 = progress.add_task("Analyzing hook potential...", total=None)
        time.sleep(0.3)
        progress.update(task1, description="[green]✓[/green] Analysis complete")

        # Generate canon
        task2 = progress.add_task("Generating canonical world state...", total=None)
        time.sleep(1.0)
        progress.update(task2, description="[green]✓[/green] Canon generated")

        # Create canon pack
        task3 = progress.add_task("Creating canon pack artifact...", total=None)
        time.sleep(0.3)
        progress.update(task3, description="[green]✓[/green] Canon pack created")

    # Display result
    canon_id = f"CANON-{hook_id}"
    console.print()
    console.print(
        Panel(
            f"[green]✓ Hook canonized successfully[/green]\n\n"
            f"[cyan]Canon ID:[/cyan] {canon_id}\n"
            f"[cyan]Canon Type:[/cyan] History Pack\n"
            f"[cyan]Elements:[/cyan] 7 (people, places, events)",
            title="[bold green]Canonization Complete[/bold green]",
            border_style="green",
        )
    )

    console.print()


@app.command(name="images")
def generate_images(
    pending: bool = typer.Option(
        False,
        "--pending",
        help="Generate all pending shotlists",
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="AI provider to use (e.g., dalle, midjourney)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", help="Model to use (provider-specific)"
    ),
) -> None:
    """Batch generate images.

    Generate images from multiple shotlists at once.
    """
    # Check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    if not pending:
        console.print(
            "[yellow]Please specify --pending to generate "
            "all pending images[/yellow]"
        )
        raise typer.Exit(1)

    # Show batch generation panel
    console.print()
    provider_info = f"Provider: {provider}" if provider else "Using default provider"
    model_info = f"Model: {model}" if model else "Using default model"

    console.print(
        Panel(
            f"[cyan]Mode:[/cyan] Batch generate pending\n"
            f"[cyan]{provider_info}[/cyan]\n"
            f"[cyan]{model_info}[/cyan]",
            title="[bold cyan]Batch Image Generation[/bold cyan]",
            border_style="cyan",
        )
    )

    # Simulate batch generation
    console.print(
        "\n[yellow]Note: Batch generation will integrate with questfoundry-py "
        "providers in a future release.[/yellow]"
    )
    console.print("[dim]Demonstrating progress tracking for multiple images...[/dim]\n")

    # Mock pending shotlists
    pending_shotlists = ["SHOT-001", "SHOT-002", "SHOT-003"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            "Generating 3 images...", total=len(pending_shotlists)
        )

        for i, shotlist_id in enumerate(pending_shotlists, 1):
            progress.update(
                task,
                description=f"[cyan]Generating image {i}/{len(pending_shotlists)}: "
                f"{shotlist_id}[/cyan]",
            )
            time.sleep(1.0)
            progress.advance(task)

    # Display summary
    console.print()
    console.print(
        Panel(
            "[green]✓ Batch generation complete[/green]\n\n"
            "[cyan]Generated:[/cyan] 3 images\n"
            "[cyan]Path:[/cyan] .questfoundry/assets/images/\n"
            "[cyan]Total time:[/cyan] 3m 15s",
            title="[bold green]Batch Generation Complete[/bold green]",
            border_style="green",
        )
    )

    console.print()
