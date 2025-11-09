"""Progress indicators for long-running operations"""

import time
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

console = Console()


@contextmanager
def loop_progress(loop_name: str, description: str | None = None):
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
def step_progress(steps: list[str]):
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

        def advance(description: str | None = None):
            if description:
                progress.update(task, description=description)
            progress.advance(task)

        try:
            yield progress, task, advance
        finally:
            progress.update(task, completed=True)


def show_spinner(message: str):
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

    def start_activity(self, activity: str):
        """Start tracking a new activity"""
        self.current_activity = activity
        self.activities.append(
            {"activity": activity, "start": time.time(), "end": None, "status": "running"}
        )
        console.print(f"[cyan]→ {activity}[/cyan]")

    def complete_activity(self, status: str = "completed"):
        """Mark current activity as complete"""
        if self.activities:
            self.activities[-1]["end"] = time.time()
            self.activities[-1]["status"] = status
            elapsed = self.activities[-1]["end"] - self.activities[-1]["start"]
            if status == "completed":
                console.print(f"[green]✓ {self.current_activity} ({elapsed:.1f}s)[/green]")
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
