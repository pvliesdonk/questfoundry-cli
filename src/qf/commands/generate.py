"""Asset generation commands"""

import json
from pathlib import Path
from typing import Any, Optional, cast

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from qf.completions import complete_artifact_ids, complete_provider_names
from qf.utils import find_project_file
from qf.utils.workspace import get_workspace, QUESTFOUNDRY_AVAILABLE
from qf.utils.providers import get_role_registry

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
    shotlist_id: str = typer.Argument(
        ..., help="Shotlist artifact ID", autocompletion=complete_artifact_ids
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        help="AI provider to use (e.g., dalle, midjourney)",
        autocompletion=complete_provider_names,
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

    # Real generation with questfoundry-py integration
    if not QUESTFOUNDRY_AVAILABLE:
        console.print(
            "\n[red]Error: questfoundry-py is not installed.[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)

    try:
        from questfoundry.roles import RoleContext
        from questfoundry.models import Artifact

        # Get workspace and role registry
        ws = get_workspace()
        role_registry = get_role_registry()

        # Convert dict artifact to Artifact model
        artifact_obj = Artifact(
            type=artifact.get("type", "shotlist"),
            data=artifact.get("data", artifact),
            metadata=artifact.get("metadata", {"id": shotlist_id}),
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Initialize Illustrator role
            task1 = progress.add_task("Initializing Illustrator role...", total=None)
            illustrator = role_registry.get_role("illustrator")
            progress.update(task1, description="[green]✓[/green] Role initialized")

            # Generate image
            task2 = progress.add_task(
                "Generating image (this may take a moment)...", total=None
            )

            context = RoleContext(
                task="create_render",
                artifacts=[artifact_obj],
                workspace_path=ws.path,
                additional_context={
                    "shotlist": artifact,
                    "provider": provider,
                    "model": model,
                },
            )

            result = illustrator.execute_task(context)

            if not result.success:
                progress.stop()
                console.print(f"\n[red]Error: {result.error}[/red]")
                raise typer.Exit(1)

            progress.update(task2, description="[green]✓[/green] Image generated")

            # Save generated artifacts to workspace
            task3 = progress.add_task("Saving artifacts to workspace...", total=None)
            for generated_artifact in result.artifacts:
                ws.save_hot_artifact(generated_artifact)
            progress.update(task3, description="[green]✓[/green] Artifacts saved")

        # Display result
        artifact_ids = [a.artifact_id for a in result.artifacts if a.artifact_id]
        result_path = ".questfoundry/hot/"

        console.print()
        console.print(
            Panel(
                f"[green]✓ Image generated successfully[/green]\n\n"
                f"[cyan]Artifacts:[/cyan] {', '.join(artifact_ids) if artifact_ids else 'Generated'}\n"
                f"[cyan]Location:[/cyan] {result_path}\n"
                f"[cyan]Role:[/cyan] Illustrator",
                title="[bold green]Generation Complete[/bold green]",
                border_style="green",
            )
        )

    except ImportError as e:
        console.print(
            f"\n[red]Error: Failed to import questfoundry-py components: {e}[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error during generation: {e}[/red]")
        raise typer.Exit(1)

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

    # Real generation with questfoundry-py integration
    if not QUESTFOUNDRY_AVAILABLE:
        console.print(
            "\n[red]Error: questfoundry-py is not installed.[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)

    try:
        from questfoundry.roles import RoleContext
        from questfoundry.models import Artifact

        # Get workspace and role registry
        ws = get_workspace()
        role_registry = get_role_registry()

        # Convert dict artifact to Artifact model
        artifact_obj = Artifact(
            type=artifact.get("type", "cuelist"),
            data=artifact.get("data", artifact),
            metadata=artifact.get("metadata", {"id": cuelist_id}),
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Initialize AudioProducer role
            task1 = progress.add_task("Initializing Audio Producer role...", total=None)
            audio_producer = role_registry.get_role("audio_producer")
            progress.update(task1, description="[green]✓[/green] Role initialized")

            # Generate audio
            task2 = progress.add_task(
                "Generating audio (this may take a moment)...", total=None
            )

            context = RoleContext(
                task="create_asset",
                artifacts=[artifact_obj],
                workspace_path=ws.path,
                additional_context={
                    "cuelist": artifact,
                    "provider": provider,
                },
            )

            result = audio_producer.execute_task(context)

            if not result.success:
                progress.stop()
                console.print(f"\n[red]Error: {result.error}[/red]")
                raise typer.Exit(1)

            progress.update(task2, description="[green]✓[/green] Audio generated")

            # Save generated artifacts to workspace
            task3 = progress.add_task("Saving audio to workspace...", total=None)
            for generated_artifact in result.artifacts:
                ws.save_hot_artifact(generated_artifact)
            progress.update(task3, description="[green]✓[/green] Audio saved")

        # Display result
        artifact_ids = [a.artifact_id for a in result.artifacts if a.artifact_id]
        result_path = ".questfoundry/hot/"

        console.print()
        console.print(
            Panel(
                f"[green]✓ Audio generated successfully[/green]\n\n"
                f"[cyan]Artifacts:[/cyan] {', '.join(artifact_ids) if artifact_ids else 'Generated'}\n"
                f"[cyan]Location:[/cyan] {result_path}\n"
                f"[cyan]Role:[/cyan] Audio Producer",
                title="[bold green]Generation Complete[/bold green]",
                border_style="green",
            )
        )

    except ImportError as e:
        console.print(
            f"\n[red]Error: Failed to import questfoundry-py components: {e}[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error during generation: {e}[/red]")
        raise typer.Exit(1)

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

    # Real generation with questfoundry-py integration
    if not QUESTFOUNDRY_AVAILABLE:
        console.print(
            "\n[red]Error: questfoundry-py is not installed.[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)

    try:
        from questfoundry.roles import RoleContext
        from questfoundry.models import Artifact

        # Get workspace and role registry
        ws = get_workspace()
        role_registry = get_role_registry()

        # Convert dict artifact to Artifact model
        artifact_obj = Artifact(
            type=artifact.get("type", "tu"),
            data=artifact.get("data", artifact),
            metadata=artifact.get("metadata", {"id": tu_id}),
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Initialize SceneSmith role
            task1 = progress.add_task("Initializing Scene Smith role...", total=None)
            scene_smith = role_registry.get_role("scene_smith")
            progress.update(task1, description="[green]✓[/green] Role initialized")

            # Generate scene prose
            task2 = progress.add_task("Generating scene prose...", total=None)

            context = RoleContext(
                task="draft_scene",
                artifacts=[artifact_obj],
                workspace_path=ws.path,
                additional_context={
                    "tu": artifact,
                    "provider": provider,
                },
            )

            result = scene_smith.execute_task(context)

            if not result.success:
                progress.stop()
                console.print(f"\n[red]Error: {result.error}[/red]")
                raise typer.Exit(1)

            progress.update(task2, description="[green]✓[/green] Prose generated")

            # Save generated artifacts to workspace
            task3 = progress.add_task("Saving scene to workspace...", total=None)
            for generated_artifact in result.artifacts:
                ws.save_hot_artifact(generated_artifact)
            progress.update(task3, description="[green]✓[/green] Scene saved")

        # Display result
        artifact_ids = [a.artifact_id for a in result.artifacts if a.artifact_id]
        result_path = ".questfoundry/hot/"

        # Extract preview from result output
        preview = result.output[:150] + "..." if len(result.output) > 150 else result.output

        console.print()
        console.print(
            Panel(
                f"[green]✓ Scene prose generated successfully[/green]\n\n"
                f"[cyan]Artifacts:[/cyan] {', '.join(artifact_ids) if artifact_ids else 'Generated'}\n"
                f"[cyan]Location:[/cyan] {result_path}\n"
                f"[cyan]Role:[/cyan] Scene Smith",
                title="[bold green]Generation Complete[/bold green]",
                border_style="green",
            )
        )

        if preview:
            console.print(f"\n[cyan]Preview:[/cyan]\n[dim]{preview}[/dim]\n")

    except ImportError as e:
        console.print(
            f"\n[red]Error: Failed to import questfoundry-py components: {e}[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error during generation: {e}[/red]")
        raise typer.Exit(1)


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

    # Real canonization with questfoundry-py integration
    if not QUESTFOUNDRY_AVAILABLE:
        console.print(
            "\n[red]Error: questfoundry-py is not installed.[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)

    try:
        from questfoundry.roles import RoleContext
        from questfoundry.models import Artifact

        # Get workspace and role registry
        ws = get_workspace()
        role_registry = get_role_registry()

        # Convert dict artifact to Artifact model
        artifact_obj = Artifact(
            type=artifact.get("type", "hook_card"),
            data=artifact.get("data", artifact),
            metadata=artifact.get("metadata", {"id": hook_id}),
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Initialize LoreWeaver role
            task1 = progress.add_task("Initializing Lore Weaver role...", total=None)
            lore_weaver = role_registry.get_role("lore_weaver")
            progress.update(task1, description="[green]✓[/green] Role initialized")

            # Expand canon
            task2 = progress.add_task("Expanding hook to canonical lore...", total=None)

            context = RoleContext(
                task="expand_canon",
                artifacts=[artifact_obj],
                workspace_path=ws.path,
                additional_context={
                    "hook": artifact,
                    "provider": provider,
                },
            )

            result = lore_weaver.execute_task(context)

            if not result.success:
                progress.stop()
                console.print(f"\n[red]Error: {result.error}[/red]")
                raise typer.Exit(1)

            progress.update(task2, description="[green]✓[/green] Canon generated")

            # Save generated artifacts to workspace
            task3 = progress.add_task("Saving canon pack to workspace...", total=None)
            for generated_artifact in result.artifacts:
                ws.save_hot_artifact(generated_artifact)
            progress.update(task3, description="[green]✓[/green] Canon pack saved")

        # Display result
        artifact_ids = [a.artifact_id for a in result.artifacts if a.artifact_id]
        result_path = ".questfoundry/hot/canon/"

        console.print()
        console.print(
            Panel(
                f"[green]✓ Hook canonized successfully[/green]\n\n"
                f"[cyan]Artifacts:[/cyan] {', '.join(artifact_ids) if artifact_ids else 'Generated'}\n"
                f"[cyan]Location:[/cyan] {result_path}\n"
                f"[cyan]Role:[/cyan] Lore Weaver",
                title="[bold green]Canonization Complete[/bold green]",
                border_style="green",
            )
        )

    except ImportError as e:
        console.print(
            f"\n[red]Error: Failed to import questfoundry-py components: {e}[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error during canonization: {e}[/red]")
        raise typer.Exit(1)

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

    # Real batch generation with questfoundry-py integration
    if not QUESTFOUNDRY_AVAILABLE:
        console.print(
            "\n[red]Error: questfoundry-py is not installed.[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)

    try:
        from questfoundry.roles import RoleContext
        from questfoundry.models import Artifact

        # Get workspace and role registry
        ws = get_workspace()
        role_registry = get_role_registry()

        # Query workspace for pending shotlists
        pending_shotlists = ws.list_hot_artifacts(
            artifact_type="shotlist",
            filters={"status": "pending"}
        )

        if not pending_shotlists:
            console.print(
                "\n[yellow]No pending shotlists found.[/yellow]\n"
                "[cyan]Tip:[/cyan] Create shotlists with pending status to batch generate."
            )
            raise typer.Exit(0)

        console.print(f"\n[cyan]Found {len(pending_shotlists)} pending shotlist(s)[/cyan]\n")

        # Initialize Illustrator role once
        illustrator = role_registry.get_role("illustrator")

        generated_count = 0
        failed_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Generating {len(pending_shotlists)} image(s)...",
                total=len(pending_shotlists),
            )

            for i, shotlist in enumerate(pending_shotlists, 1):
                shotlist_id = shotlist.artifact_id or f"shotlist-{i}"

                progress.update(
                    task,
                    description=f"[cyan]Generating image {i}/{len(pending_shotlists)}: "
                    f"{shotlist_id}[/cyan]",
                )

                try:
                    context = RoleContext(
                        task="create_render",
                        artifacts=[shotlist],
                        workspace_path=ws.path,
                        additional_context={
                            "provider": provider,
                            "model": model,
                        },
                    )

                    result = illustrator.execute_task(context)

                    if result.success:
                        # Save generated artifacts
                        for generated_artifact in result.artifacts:
                            ws.save_hot_artifact(generated_artifact)
                        generated_count += 1
                    else:
                        console.print(
                            f"\n[red]Failed to generate {shotlist_id}: {result.error}[/red]"
                        )
                        failed_count += 1

                except Exception as e:
                    console.print(f"\n[red]Error generating {shotlist_id}: {e}[/red]")
                    failed_count += 1

                progress.advance(task)

        # Display summary
        console.print()
        console.print(
            Panel(
                f"[green]✓ Batch generation complete[/green]\n\n"
                f"[cyan]Generated:[/cyan] {generated_count} image(s)\n"
                f"[cyan]Failed:[/cyan] {failed_count}\n"
                f"[cyan]Location:[/cyan] .questfoundry/hot/",
                title="[bold green]Batch Generation Complete[/bold green]",
                border_style="green",
            )
        )

    except ImportError as e:
        console.print(
            f"\n[red]Error: Failed to import questfoundry-py components: {e}[/red]\n"
            "[yellow]Install with:[/yellow] pip install questfoundry-py[openai]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error during batch generation: {e}[/red]")
        raise typer.Exit(1)

    console.print()
