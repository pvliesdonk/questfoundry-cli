"""Command utilities and decorators for QuestFoundry CLI"""

from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

import typer
from rich.console import Console

from .project import find_project_file

FuncType = TypeVar("FuncType", bound=Callable[..., Any])


class BindFormat(str, Enum):
    """Format options for bind command"""

    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"


class ExportFormat(str, Enum):
    """Format options for export command"""

    HTML = "html"
    MARKDOWN = "markdown"


def require_project(func: FuncType) -> FuncType:
    """Decorator to ensure a QuestFoundry project exists.

    Exits with error code 1 if no project file is found in current directory.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Check for project file before executing command"""
        project_file = find_project_file()
        if not project_file:
            console = Console()
            console.print(
                "[red]Error: No QuestFoundry project found in current directory.[/red]"
            )
            raise typer.Exit(1)
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
