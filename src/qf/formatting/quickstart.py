"""Quickstart-specific formatting and display utilities."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()


def display_quickstart_header(project_name: str) -> None:
    """Display quickstart header with project name.

    Args:
        project_name: Name of the project
    """
    console.print()
    console.print(
        Panel(
            f"[bold cyan]QuestFoundry Quickstart[/bold cyan]",
            title=f"[bold]{project_name}[/bold]",
            border_style="cyan",
        )
    )
    console.print()


def display_completed_loops(loops: list[str]) -> None:
    """Display list of completed loops.

    Args:
        loops: List of completed loop names
    """
    console.print("[bold cyan]Completed Loops:[/bold cyan]")
    tree = Tree("")
    for loop in loops:
        tree.add(f"[green]✓[/green] {loop}")
    console.print(tree)
    console.print()


def display_showrunner_suggestion(
    loop_name: str,
    reasoning: str,
) -> None:
    """Display Showrunner's loop suggestion with reasoning.

    Args:
        loop_name: Suggested loop name
        reasoning: Explanation for why this loop is suggested
    """
    console.print()
    console.print(
        Panel(
            f"[cyan]Suggested Loop:[/cyan] {loop_name}\n\n"
            f"[cyan]Reasoning:[/cyan]\n"
            f"{reasoning}",
            title="[bold cyan]Showrunner Decision[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()


def display_loop_goal(loop_name: str, will_accomplish: list[str], will_not: list[str]) -> None:
    """Display loop purpose and scope boundaries.

    Args:
        loop_name: Name of the loop
        will_accomplish: List of things the loop will accomplish
        will_not: List of things the loop will NOT do
    """
    console.print()

    will_text = "\n".join(f"  [green]✓[/green] {item}" for item in will_accomplish)
    not_text = "\n".join(f"  [red]✗[/red] {item}" for item in will_not)

    content = (
        f"[cyan]Purpose:[/cyan] {loop_name}\n\n"
        f"[cyan]This loop WILL:[/cyan]\n"
        f"{will_text}\n\n"
        f"[cyan]This loop will NOT:[/cyan]\n"
        f"{not_text}"
    )

    console.print(
        Panel(
            content,
            title=f"[bold]Loop Scope: {loop_name}[/bold]",
            border_style="cyan",
        )
    )
    console.print()


def display_completion_message(
    project_name: str,
    completed_loops: list[str],
    total_time: str,
) -> None:
    """Display quickstart completion message.

    Args:
        project_name: Name of completed project
        completed_loops: List of loops that were executed
        total_time: Total elapsed time
    """
    loops_text = "\n".join(f"  [green]✓[/green] {loop}" for loop in completed_loops)

    console.print()
    console.print(
        Panel(
            f"[bold green]Quickstart Complete![/bold green]\n\n"
            f"[cyan]Project:[/cyan] {project_name}\n"
            f"[cyan]Loops Completed:[/cyan]\n"
            f"{loops_text}\n\n"
            f"[cyan]Total Time:[/cyan] {total_time}\n\n"
            f"[yellow]Next Steps:[/yellow]\n"
            f"  [cyan]View status: [green]qf status[/green][/cyan]\n"
            f"  [cyan]List artifacts: [green]qf list[/green][/cyan]\n"
            f"  [cyan]Run more loops: [green]qf run <loop-name>[/green][/cyan]",
            border_style="green",
        )
    )
    console.print()


def create_loop_progress_table(
    completed: list[str],
    current: str | None = None,
    pending: list[str] | None = None,
) -> Table:
    """Create progress table for quickstart loops.

    Args:
        completed: List of completed loop names
        current: Currently executing loop name
        pending: List of pending loop names

    Returns:
        Rich Table showing progress
    """
    table = Table(title="Loop Progress")
    table.add_column("Status", style="magenta")
    table.add_column("Loop", style="cyan")

    for loop in completed:
        table.add_row("[green]✓[/green]", loop)

    if current:
        table.add_row("[yellow]▶[/yellow]", current)

    if pending:
        for loop in pending:
            table.add_row("[gray]○[/gray]", loop)

    return table


def display_artifact_summary(artifact_count: int, artifact_types: dict[str, int]) -> None:
    """Display summary of artifacts created during quickstart.

    Args:
        artifact_count: Total number of artifacts
        artifact_types: Dictionary mapping type to count
    """
    console.print()
    console.print(f"[cyan]Artifacts Created:[/cyan] {artifact_count}\n")

    table = Table(title="Artifacts by Type")
    table.add_column("Type", style="cyan")
    table.add_column("Count", style="magenta")

    for artifact_type, count in artifact_types.items():
        table.add_row(artifact_type, str(count))

    console.print(table)
    console.print()


def display_resume_checkpoint(loops_completed: list[str], last_loop: str) -> None:
    """Display message when resuming from checkpoint.

    Args:
        loops_completed: List of previously completed loops
        last_loop: Last loop that was being executed
    """
    console.print()
    console.print(
        Panel(
            f"[cyan]Resuming Quickstart[/cyan]\n\n"
            f"[cyan]Previously Completed:[/cyan]\n"
            + "\n".join(f"  [green]✓[/green] {loop}" for loop in loops_completed)
            + f"\n\n[cyan]Last Loop:[/cyan] {last_loop}",
            border_style="cyan",
        )
    )
    console.print()
