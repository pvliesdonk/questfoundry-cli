"""Showrunner decision display and formatting.

Handles communication of Showrunner's orchestration decisions,
including which loops to run, which steps to revise, and why.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def show_showrunner_decision(decision: str, reasoning: str = "") -> None:
    """Display a Showrunner decision with optional reasoning.

    Args:
        decision: Description of the decision being made
        reasoning: Optional explanation of why this decision was made
    """
    text = Text()
    text.append("⟳ Showrunner: ", style="bold yellow")
    text.append(decision, style="yellow")

    if reasoning:
        text.append("\n\n", style="dim")
        text.append("Reasoning:\n", style="bold dim")
        text.append(reasoning, style="dim")

    console.print(Panel(text, border_style="yellow"))
    console.print()


def show_revision_plan(steps_to_revise: list[str], reason: str = "") -> None:
    """Display which steps Showrunner plans to revise.

    Args:
        steps_to_revise: List of step names to revise
        reason: Optional reason for the revision
    """
    text = Text()
    text.append("Revising steps: ", style="bold yellow")
    text.append(", ".join(steps_to_revise), style="yellow")

    if reason:
        text.append("\n\n", style="dim")
        text.append(f"Reason: {reason}", style="dim")

    console.print(Panel(text, border_style="yellow", title="Revision Plan"))
    console.print()


def show_loop_suggestion(loop_name: str, reason: str = "") -> None:
    """Display Showrunner's suggestion for the next loop.

    Args:
        loop_name: Display name of suggested loop
        reason: Optional reason for the suggestion
    """
    text = Text()
    text.append("Showrunner suggests: ", style="bold cyan")
    text.append(loop_name, style="cyan")

    if reason:
        text.append("\n\n", style="dim")
        text.append("Reason: ", style="bold dim")
        text.append(reason, style="dim")

    console.print(Panel(text, border_style="cyan", title="Next Loop Suggestion"))
    console.print()


def show_collaboration_request(
    step_name: str, requested_agent: str, reason: str = ""
) -> None:
    """Display a request for agent collaboration during a step.

    Args:
        step_name: Step requesting collaboration
        requested_agent: Agent being requested
        reason: Optional reason for the collaboration request
    """
    text = Text()
    text.append(f"Step '{step_name}' requests collaboration with ", style="cyan")
    text.append(requested_agent, style="bold cyan")

    if reason:
        text.append("\n\n", style="dim")
        text.append("Reason: ", style="bold dim")
        text.append(reason, style="dim")

    console.print(Panel(text, border_style="cyan", title="Collaboration Request"))
    console.print()


def show_quality_gate_failure(
    step_name: str, issues: list[str], showrunner_plan: str = ""
) -> None:
    """Display quality gate failure and Showrunner's plan to remediate.

    Args:
        step_name: Step that triggered the quality gate failure
        issues: List of issues found by the quality gate
        showrunner_plan: Showrunner's plan to fix the issues
    """
    text = Text()
    text.append(f"Step '{step_name}' blocked by quality gate\n\n", style="bold red")
    text.append("Issues found:\n", style="bold red")

    for issue in issues:
        text.append(f"  • {issue}\n", style="red")

    if showrunner_plan:
        text.append("\n", style="dim")
        text.append("Showrunner's plan:\n", style="bold yellow")
        text.append(showrunner_plan, style="yellow")

    console.print(Panel(text, border_style="red", title="Quality Gate Failure"))
    console.print()


def show_stabilization_achieved() -> None:
    """Display message that loop has achieved stabilization."""
    text = Text()
    text.append("✓ Loop Stabilized", style="bold green")

    console.print(Panel(text, border_style="green", title="Stabilization"))
    console.print()
