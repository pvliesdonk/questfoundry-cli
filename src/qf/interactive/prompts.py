"""User prompts and questions for interactive mode."""

import sys
from typing import Optional

import questionary
from rich.console import Console

# Initialize Console defensively for non-TTY environments
console = Console(
    force_terminal=sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False
)


def _is_interactive() -> bool:
    """Check if we're in an interactive TTY environment.

    Returns:
        True if both stdin and stdout are TTYs, False otherwise
    """
    return (
        hasattr(sys.stdin, "isatty")
        and hasattr(sys.stdout, "isatty")
        and sys.stdin.isatty()
        and sys.stdout.isatty()
    )


def ask_premise() -> str:
    """Ask user for story premise.

    Returns:
        Story premise text (at least 10 characters)

    Raises:
        RuntimeError: If not in an interactive TTY environment
    """
    if not _is_interactive():
        raise RuntimeError(
            "Interactive mode requires a TTY. "
            "Please run 'qf quickstart' in an interactive terminal."
        )

    return questionary.text(
        "What is your story premise?",
        validate=lambda x: len(x) >= 10 or "Please provide at least 10 characters",
    ).ask() or ""


def ask_tone() -> str:
    """Ask user for story tone/genre.

    Returns:
        Selected tone (mystery, horror, adventure, sci-fi, romance, fantasy)

    Raises:
        RuntimeError: If not in an interactive TTY environment
    """
    if not _is_interactive():
        raise RuntimeError(
            "Interactive mode requires a TTY. "
            "Please run 'qf quickstart' in an interactive terminal."
        )

    return questionary.select(
        "What tone or genre?",
        choices=[
            "Mystery",
            "Horror",
            "Adventure",
            "Science Fiction",
            "Romance",
            "Fantasy",
            "Thriller",
            "Drama",
        ],
    ).ask() or "Adventure"


def ask_length() -> str:
    """Ask user for story length/scope.

    Returns:
        Selected length (short, medium, long)

    Raises:
        RuntimeError: If not in an interactive TTY environment
    """
    if not _is_interactive():
        raise RuntimeError(
            "Interactive mode requires a TTY. "
            "Please run 'qf quickstart' in an interactive terminal."
        )

    return questionary.select(
        "How long should the story be?",
        choices=[
            "Short Story (5-20 pages)",
            "Novella (20-50 pages)",
            "Novel (50+ pages)",
        ],
    ).ask() or "Novella"


def ask_project_name(premise: str) -> str:
    """Ask user for project name (with default based on premise).

    Args:
        premise: Story premise to suggest a default name

    Returns:
        Project name

    Raises:
        RuntimeError: If not in an interactive TTY environment
    """
    if not _is_interactive():
        raise RuntimeError(
            "Interactive mode requires a TTY. "
            "Please run 'qf quickstart' in an interactive terminal."
        )

    # Create a default name from premise
    default_name = "-".join(premise.split()[:3]).lower()[:30]

    return questionary.text(
        "Project name",
        default=default_name,
        validate=lambda x: len(x) >= 3 or "Name must be at least 3 characters",
    ).ask() or default_name


def confirm_setup(premise: str, tone: str, length: str, name: str) -> bool:
    """Confirm setup before creating project.

    Args:
        premise: Story premise
        tone: Selected tone
        length: Selected length
        name: Project name

    Returns:
        True if user confirms, False otherwise

    Raises:
        RuntimeError: If not in an interactive TTY environment
    """
    if not _is_interactive():
        raise RuntimeError(
            "Interactive mode requires a TTY. "
            "Please run 'qf quickstart' in an interactive terminal."
        )

    # Display formatted setup summary
    console.print()
    console.print("[cyan]Project Setup[/cyan]")
    console.print(f"[cyan]Name:[/cyan] {name}")
    console.print(f"[cyan]Premise:[/cyan] {premise}")
    console.print(f"[cyan]Tone:[/cyan] {tone}")
    console.print(f"[cyan]Length:[/cyan] {length}")

    return questionary.confirm(
        "Create project?",
        auto_enter=True,
        default=True,
    ).ask() or False


def ask_review_artifacts() -> bool:
    """Ask user if they want to review artifacts.

    Returns:
        True if user wants to review, False otherwise

    Raises:
        RuntimeError: If not in an interactive TTY environment
    """
    if not _is_interactive():
        raise RuntimeError(
            "Interactive mode requires a TTY. "
            "Please run 'qf quickstart' in an interactive terminal."
        )

    return questionary.confirm(
        "Review artifacts?",
        auto_enter=True,
        default=False,
    ).ask() or False


def ask_continue_loop(next_loop: str) -> bool:
    """Ask user if they want to continue with suggested loop.

    Args:
        next_loop: Name of suggested loop

    Returns:
        True to continue, False to exit

    Raises:
        RuntimeError: If not in an interactive TTY environment
    """
    if not _is_interactive():
        raise RuntimeError(
            "Interactive mode requires a TTY. "
            "Please run 'qf quickstart' in an interactive terminal."
        )

    return questionary.confirm(
        f"Continue with {next_loop}?",
        auto_enter=True,
        default=True,
    ).ask() or False


def ask_agent_response(question: str, suggestions: Optional[list[str]] = None) -> str:
    """Ask user to respond to agent question during interactive mode.

    Args:
        question: The agent's question
        suggestions: Optional list of suggested responses

    Returns:
        User's response text

    Raises:
        RuntimeError: If not in an interactive TTY environment
    """
    if not _is_interactive():
        raise RuntimeError(
            "Interactive mode requires a TTY. "
            "Please run 'qf quickstart' in an interactive terminal."
        )

    if suggestions:
        # Show suggestions as a select menu
        choices = suggestions + ["Other (type custom response)"]
        response = questionary.select(
            question,
            choices=choices,
        ).ask()

        if response == "Other (type custom response)":
            return questionary.text(
                "Your response:",
                validate=lambda x: len(x) > 0 or "Response cannot be empty",
            ).ask() or ""

        return response or ""
    else:
        # Free-form text input
        return questionary.text(
            question,
            validate=lambda x: len(x) > 0 or "Response cannot be empty",
        ).ask() or ""
