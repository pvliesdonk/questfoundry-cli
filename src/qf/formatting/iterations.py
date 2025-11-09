"""Iteration summary and history display.

Shows detailed iteration-by-iteration progress including step counts,
revisions, blockers, and overall efficiency metrics.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from qf.formatting.loop_progress import Iteration, LoopProgressTracker

console = Console()


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "2m 34s" or "45s"
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def display_iteration_header(iteration: Iteration) -> None:
    """Display header for an iteration.

    Args:
        iteration: Iteration object to display
    """
    title = f"Iteration {iteration.iteration_number}"
    if iteration.duration:
        title += f" ({format_duration(iteration.duration)})"

    separator = "━" * 80
    console.print(f"\n{separator}")
    console.print(f"[bold]{title}[/bold]")
    console.print(f"{separator}\n")


def display_iteration_steps(iteration: Iteration) -> None:
    """Display step-by-step progress for an iteration.

    Args:
        iteration: Iteration object to display
    """
    for step in iteration.steps:
        # Step icon and name
        if step.blocked:
            icon = "✗"
            color = "red"
            status_text = "[red]BLOCKED[/red]"
        elif step.status == "completed":
            icon = "✓" if not step.is_revision else "↻"
            color = "green"
            status_text = "[green]completed[/green]"
        else:
            icon = "→"
            color = "yellow"
            status_text = "[yellow]running[/yellow]"

        # Revision indicator
        revision_indicator = " (revision)" if step.is_revision else ""

        # Duration if available
        duration_text = ""
        if step.duration > 0:
            duration_text = f" ({format_duration(step.duration)})"

        # Display step line
        step_line = f"[{color}]{icon}[/{color}] {step.name}{revision_indicator}"
        agent_text = f"({step.agent})" if step.agent else ""

        console.print(f"{step_line} {agent_text}{duration_text}")

        # Show blocking issues if blocked
        if step.blocked and step.blocking_issues:
            console.print("[red]  Issues:[/red]")
            for issue in step.blocking_issues:
                console.print(f"  [red]  - {issue}[/red]")


def display_iteration_summary(iteration: Iteration) -> None:
    """Display summary statistics for an iteration.

    Args:
        iteration: Iteration object to summarize
    """
    text = Text()

    # Step counts
    text.append(f"Steps: {iteration.completed_steps} completed", style="green")
    if iteration.blocked_steps > 0:
        text.append(f" | {iteration.blocked_steps} blocked", style="red")

    # Revision info
    if iteration.revised_steps > 0:
        text.append(f" | {iteration.revised_steps} revisions", style="yellow")

    # Stabilization status
    text.append("\n")
    if iteration.stabilized:
        text.append("Status: ", style="bold")
        text.append("Stabilized", style="green")
    elif iteration.blocked_steps > 0:
        text.append("Status: ", style="bold")
        text.append("Blocked", style="red")
    else:
        text.append("Status: ", style="bold")
        text.append("In Progress", style="yellow")

    # Showrunner decision
    if iteration.showrunner_decision:
        text.append("\n\n")
        text.append("Showrunner decision:\n", style="bold dim")
        text.append(iteration.showrunner_decision, style="dim")

    console.print(Panel(text, border_style="cyan"))
    console.print()


def display_full_iteration_history(tracker: LoopProgressTracker) -> None:
    """Display complete iteration history for a loop.

    Shows all iterations with step details and summary for each.

    Args:
        tracker: LoopProgressTracker containing iteration history
    """
    if not tracker.iterations:
        console.print("[yellow]No iterations recorded[/yellow]\n")
        return

    # Only show for multi-iteration loops
    if not tracker.is_multi_iteration:
        return

    console.print("\n[bold cyan]Iteration Summary[/bold cyan]\n")

    for iteration in tracker.iterations:
        display_iteration_header(iteration)
        display_iteration_steps(iteration)
        display_iteration_summary(iteration)


def display_efficiency_metrics(tracker: LoopProgressTracker) -> None:
    """Display efficiency metrics for multi-iteration loops.

    Shows step reuse percentage and other efficiency indicators.

    Args:
        tracker: LoopProgressTracker containing execution data
    """
    if not tracker.is_multi_iteration or len(tracker.iterations) < 2:
        return

    # Calculate metrics
    total_steps = sum(len(i.steps) for i in tracker.iterations)
    revised_steps = sum(i.revised_steps for i in tracker.iterations)
    reused_steps = total_steps - revised_steps

    efficiency_percent = (reused_steps / total_steps * 100) if total_steps > 0 else 0

    text = Text()
    text.append("Efficiency Metrics\n", style="bold cyan")
    text.append(f"\nTotal step executions: {total_steps}\n", style="cyan")
    text.append(f"Step revisions: {revised_steps}\n", style="yellow")
    text.append(f"Step reuse: {reused_steps} ({efficiency_percent:.0f}%)\n", style="green")
    text.append(f"Total duration: {format_duration(tracker.total_duration)}", style="cyan")

    console.print(Panel(text, border_style="cyan", title="Performance"))
    console.print()


def display_iteration_tree(tracker: LoopProgressTracker) -> None:
    """Display iteration history as a tree.

    Args:
        tracker: LoopProgressTracker containing iteration data
    """
    if not tracker.iterations:
        return

    tree = Tree(f"[bold]{tracker.loop_name}[/bold]")

    for iteration in tracker.iterations:
        iteration_label = f"[cyan]Iteration {iteration.iteration_number}[/cyan]"

        if iteration.duration:
            iteration_label += f" [dim]({format_duration(iteration.duration)})[/dim]"

        # Status indicator
        if iteration.stabilized:
            status = "[green]✓ Stabilized[/green]"
        elif iteration.blocked_steps > 0:
            status = "[red]✗ Blocked[/red]"
        else:
            status = "[yellow]→ In Progress[/yellow]"

        iteration_label += f" {status}"

        iteration_branch = tree.add(iteration_label)

        # Add steps as sub-items
        for step in iteration.steps:
            step_label = f"{step.name}"

            if step.is_revision:
                step_label += " [yellow](revision)[/yellow]"

            if step.duration > 0:
                step_label += f" [dim]{format_duration(step.duration)}[/dim]"

            # Step status icon
            if step.blocked:
                icon = "[red]✗[/red]"
            elif step.status == "completed":
                icon = "[green]✓[/green]"
            else:
                icon = "[yellow]→[/yellow]"

            iteration_branch.add(f"{icon} {step_label}")

    console.print(tree)
    console.print()
