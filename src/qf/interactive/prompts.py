"""User prompts and questions for interactive mode."""

from typing import Optional

import questionary


def ask_premise() -> str:
    """Ask user for story premise.

    Returns:
        Story premise text (at least 10 characters)
    """
    return questionary.text(
        "What is your story premise?",
        validate=lambda x: len(x) >= 10 or "Please provide at least 10 characters",
    ).ask() or ""


def ask_tone() -> str:
    """Ask user for story tone/genre.

    Returns:
        Selected tone (mystery, horror, adventure, sci-fi, romance, fantasy)
    """
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
    """
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
    """
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
    """
    console_text = (
        f"\n[cyan]Project Setup[/cyan]\n"
        f"[cyan]Name:[/cyan] {name}\n"
        f"[cyan]Premise:[/cyan] {premise}\n"
        f"[cyan]Tone:[/cyan] {tone}\n"
        f"[cyan]Length:[/cyan] {length}\n"
    )

    return questionary.confirm(
        f"{console_text}\nCreate project?",
        auto_enter=True,
        default=True,
    ).ask() or False


def ask_review_artifacts() -> bool:
    """Ask user if they want to review artifacts.

    Returns:
        True if user wants to review, False otherwise
    """
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
    """
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
    """
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
