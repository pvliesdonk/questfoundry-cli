"""Quickstart workflow command for rapid project setup."""

import shutil
import sys

import typer
from rich.console import Console
from rich.panel import Panel

from qf.interactive import QuickstartSession
from qf.interactive.prompts import (
    ask_continue_loop,
    ask_length,
    ask_premise,
    ask_project_name,
    ask_review_artifacts,
    ask_tone,
    confirm_setup,
)
from qf.utils import find_project_file

# Initialize Console defensively for non-TTY environments
_is_tty = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False
_terminal_size = shutil.get_terminal_size(fallback=(120, 40))

console = Console(
    force_terminal=_is_tty,
    width=_terminal_size.columns,
    color_system="auto" if _is_tty else None,
)


def _display_welcome() -> None:
    """Display welcome message and quickstart overview."""
    console.print()
    console.print(
        Panel(
            "[bold cyan]Welcome to QuestFoundry Quickstart![/bold cyan]\n\n"
            "[cyan]This guided workflow will help you create "
            "a new story project[/cyan]\n"
            "[cyan]and start the creative loops.[/cyan]\n\n"
            "[yellow]Let's begin by answering a few questions.[/yellow]",
            border_style="cyan",
        )
    )
    console.print()


def _display_completion() -> None:
    """Display completion message."""
    console.print()
    console.print(
        Panel(
            "[bold green]Quickstart Complete![/bold green]\n\n"
            "[cyan]Your project has been initialized and loops executed.[/cyan]\n\n"
            "[yellow]Next steps:[/yellow]\n"
            "[cyan]• Review artifacts: [green]qf list[/green][/cyan]\n"
            "[cyan]• Show artifact details: [green]qf show "
            "<artifact-id>[/green][/cyan]\n"
            "[cyan]• Run additional loops: [green]qf run "
            "<loop-name>[/green][/cyan]\n"
            "[cyan]• Check status: [green]qf status[/green][/cyan]",
            border_style="green",
        )
    )
    console.print()


def _display_project_summary(session: QuickstartSession) -> None:
    """Display project summary and current status.

    Args:
        session: Quickstart session with project info
    """
    status = session.get_session_status()

    completed = ", ".join(status["completed_loops"]) or "None yet"

    console.print()
    console.print(
        Panel(
            f"[cyan]Project:[/cyan] {status['project_name']}\n"
            f"[cyan]Premise:[/cyan] {status['premise']}\n"
            f"[cyan]Tone:[/cyan] {status['tone']}\n"
            f"[cyan]Length:[/cyan] {status['length']}\n"
            f"[cyan]Completed Loops:[/cyan] {completed}\n"
            f"[cyan]Elapsed Time:[/cyan] {status['elapsed_time']}",
            title="[bold cyan]Project Status[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()


def _simulate_loop_execution(loop_name: str) -> None:
    """Simulate loop execution with placeholder.

    This will be replaced with actual Layer 6 Showrunner integration.

    Args:
        loop_name: Name of loop to execute
    """
    import time

    from rich.progress import Progress, SpinnerColumn, TextColumn

    console.print()
    console.print(
        Panel(
            f"[bold cyan]{loop_name}[/bold cyan]",
            title="[bold]Executing Loop[/bold]",
            border_style="cyan",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Running {loop_name}...", total=None)
        time.sleep(1.5)
        progress.update(task, description="[green]✓[/green] Loop complete")

    console.print()


def quickstart(
    guided: bool = typer.Option(
        True,
        "--guided",
        "-g",
        help="Use guided mode (default)",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Enable interactive mode for agent collaboration",
    ),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Resume from previous checkpoint",
    ),
) -> None:
    """Start guided quickstart workflow.

    The quickstart guides you through project initialization and loop execution.
    Answer setup questions, watch loops execute, and review artifacts.

    Guided mode (default): Follow a guided workflow with checkpoints.
    Interactive mode (--interactive): Collaborate with AI agents during loops.
    Resume (--resume): Continue from previous checkpoint if available.
    """
    # Check if already in a project
    if find_project_file() and not resume:
        console.print("[yellow]A project already exists in this directory.[/yellow]")
        console.print(
            "[cyan]Use [green]qf quickstart --resume[/green] to continue, or "
            "[green]cd[/green] to a different directory.[/cyan]"
        )
        raise typer.Exit(1)

    # Initialize session
    session = QuickstartSession()

    # Try to resume from checkpoint
    if resume and session.load_checkpoint():
        console.print("[green]✓[/green] Resumed from checkpoint")
        _display_project_summary(session)
    else:
        # New quickstart
        try:
            _display_welcome()

            # Ask setup questions
            premise = ask_premise()
            if not premise:
                console.print("[red]Cancelled[/red]")
                raise typer.Exit(1)

            tone = ask_tone()
            if not tone:
                console.print("[red]Cancelled[/red]")
                raise typer.Exit(1)

            length = ask_length()
            if not length:
                console.print("[red]Cancelled[/red]")
                raise typer.Exit(1)

            project_name = ask_project_name(premise)
            if not project_name:
                console.print("[red]Cancelled[/red]")
                raise typer.Exit(1)

            # Confirm setup
            if not confirm_setup(premise, tone, length, project_name):
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

            # Create project
            if not session.create_project(project_name, premise, tone, length):
                console.print("[red]Failed to create project[/red]")
                raise typer.Exit(1)

            _display_project_summary(session)
        except RuntimeError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    # Enable interactive mode if requested
    if interactive:
        session.enable_interactive_mode()
        console.print(
            "[cyan]Interactive mode enabled. "
            "Agents may ask questions during loops.[/cyan]\n"
        )

    # Main loop execution loop
    # This is a placeholder for Showrunner-driven loop sequencing
    console.print(
        "[yellow]Note: Full Showrunner integration (dynamic loop sequencing) "
        "coming with Layer 6 integration.[/yellow]\n"
    )

    suggested_loops = [
        "Hook Harvest",
        "Lore Deepening",
        "Story Spark",
    ]

    for loop_name in suggested_loops:
        try:
            # Execute loop
            _simulate_loop_execution(loop_name)
            session.complete_loop(loop_name)

            # Checkpoint
            session.save_checkpoint()

            # Ask to review artifacts
            if ask_review_artifacts():
                console.print("[cyan]Artifact review would show list here[/cyan]")
                console.print(
                    "[cyan]Tip: Use [green]qf list[/green] and [green]qf show[/green] "
                    "to inspect artifacts[/cyan]\n"
                )

            # Ask to continue
            next_loop_idx = suggested_loops.index(loop_name) + 1
            if next_loop_idx < len(suggested_loops):
                next_loop = suggested_loops[next_loop_idx]
                if not ask_continue_loop(next_loop):
                    console.print("[yellow]Quickstart paused[/yellow]")
                    console.print(
                        "[cyan]Resume with: "
                        "[green]qf quickstart --resume[/green][/cyan]"
                    )
                    raise typer.Exit(0)
            else:
                # Last loop completed
                break
        except RuntimeError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    # Completion
    _display_project_summary(session)
    _display_completion()
