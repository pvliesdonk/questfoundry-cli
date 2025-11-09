"""Progress indicators for long-running operations"""

import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

from qf.formatting.loop_progress import LoopProgressTracker

console = Console()


@contextmanager
def loop_progress(
    loop_name: str, description: str | None = None
) -> Generator[Progress, None, None]:
    """
    Context manager for displaying loop execution progress.

    Args:
        loop_name: Name of the loop being executed
        description: Optional description of the current activity

    Yields:
        Progress object for updating status

    Example:
        with loop_progress("Hook Harvest", "Generating hooks") as progress:
            # Long-running operation
            pass
    """
    desc = description or f"Executing {loop_name}..."

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(desc, total=None)
        try:
            yield progress
        finally:
            progress.update(task, completed=True)


@contextmanager
def step_progress(
    steps: list[str],
) -> Generator[tuple[Progress, TaskID, Callable[[str | None], None]], None, None]:
    """
    Context manager for multi-step progress with defined steps.

    Args:
        steps: List of step descriptions

    Yields:
        Tuple of (progress object, task ID, advance function)

    Example:
        steps = ["Loading artifacts", "Running analysis", "Generating results"]
        with step_progress(steps) as (progress, task, advance):
            for step in steps:
                # Do work for this step
                advance(step)
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Processing...", total=len(steps))

        def advance(description: str | None = None) -> None:
            if description:
                progress.update(task, description=description)
            progress.advance(task)

        try:
            yield progress, task, advance
        finally:
            progress.update(task, completed=True)


def show_spinner(message: str) -> Progress:
    """
    Show a simple spinner with a message.

    Args:
        message: Message to display with spinner

    Returns:
        Context manager for the spinner
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


class ActivityTracker:
    """Track and display activities during loop execution"""

    def __init__(self, loop_name: str):
        self.loop_name = loop_name
        self.start_time = time.time()
        self.activities: list[dict[str, Any]] = []
        self.current_activity: str | None = None

    def start_activity(self, activity: str) -> None:
        """Start tracking a new activity"""
        self.current_activity = activity
        self.activities.append(
            {
                "activity": activity,
                "start": time.time(),
                "end": None,
                "status": "running",
            }
        )
        console.print(f"[cyan]→ {activity}[/cyan]")

    def complete_activity(self, status: str = "completed") -> None:
        """Mark current activity as complete"""
        # Guard against calling complete_activity twice
        if not self.activities or self.current_activity is None:
            return

        self.activities[-1]["end"] = time.time()
        self.activities[-1]["status"] = status
        elapsed = self.activities[-1]["end"] - self.activities[-1]["start"]
        if status == "completed":
            status_msg = f"✓ {self.current_activity} ({elapsed:.1f}s)"
            console.print(f"[green]{status_msg}[/green]")
        else:
            console.print(f"[yellow]⚠ {self.current_activity} ({status})[/yellow]")
        self.current_activity = None

    def get_duration(self) -> float:
        """Get total duration in seconds"""
        return time.time() - self.start_time

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all activities"""
        return {
            "loop": self.loop_name,
            "duration": self.get_duration(),
            "activities": self.activities,
            "total_activities": len(self.activities),
        }


def display_loop_iteration_progress(
    tracker: LoopProgressTracker, current_step: str | None = None
) -> None:
    """
    Display real-time iteration progress for a loop.

    Shows current iteration and step being executed.

    Note: Currently unused. Prepared for future integration with
    questfoundry-py Showrunner for real-time progress display.

    Args:
        tracker: LoopProgressTracker with execution data
        current_step: Optional current step being executed
    """
    if not tracker.current_iteration:
        return

    iteration_num = tracker.current_iteration.iteration_number
    step_count = len(tracker.current_iteration.steps)

    if current_step:
        console.print(
            f"[cyan]→ Iteration {iteration_num}: {current_step}[/cyan]"
        )
    else:
        console.print(
            f"[cyan]→ Iteration {iteration_num} ({step_count} steps)[/cyan]"
        )


def display_loop_stabilization_status(tracker: LoopProgressTracker) -> None:
    """
    Display loop stabilization status.

    Shows whether loop has stabilized and total iteration count.

    Note: Currently unused. Prepared for future integration to display
    final stabilization status in interactive or streaming modes.

    Args:
        tracker: LoopProgressTracker with execution data
    """
    if tracker.stabilized:
        iteration_text = (
            f"in {len(tracker.iterations)} iteration"
            if len(tracker.iterations) == 1
            else f"in {len(tracker.iterations)} iterations"
        )
        console.print(
            f"[green]✓ Loop stabilized {iteration_text}[/green]"
        )
    elif len(tracker.iterations) > 1:
        console.print(
            f"[yellow]⚠ Loop in progress ({len(tracker.iterations)} "
            f"iterations so far)[/yellow]"
        )
