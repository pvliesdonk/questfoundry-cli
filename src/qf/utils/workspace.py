"""Workspace utility functions for questfoundry-py integration"""

from pathlib import Path
from typing import Optional

from rich.console import Console

try:
    from questfoundry.state import WorkspaceManager
    QUESTFOUNDRY_AVAILABLE = True
except ImportError:
    QUESTFOUNDRY_AVAILABLE = False
    WorkspaceManager = None

console = Console()


def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the project root by looking for .questfoundry directory.

    Searches upward from start_path (or cwd) until finding .questfoundry/
    or reaching the filesystem root.

    Args:
        start_path: Starting directory (defaults to current working directory)

    Returns:
        Path to project root, or None if not found
    """
    current = start_path or Path.cwd()
    current = current.resolve()

    # Check current directory and all parents
    for directory in [current, *current.parents]:
        questfoundry_dir = directory / ".questfoundry"
        if questfoundry_dir.exists() and questfoundry_dir.is_dir():
            return directory

    return None


def get_workspace(path: Optional[Path] = None) -> "WorkspaceManager":
    """
    Get WorkspaceManager for the current or specified project.

    Args:
        path: Optional path to start search from (defaults to cwd)

    Returns:
        WorkspaceManager instance

    Raises:
        RuntimeError: If questfoundry-py is not installed
        RuntimeError: If not in a QuestFoundry project
    """
    if not QUESTFOUNDRY_AVAILABLE:
        raise RuntimeError(
            "questfoundry-py library is not installed. "
            "Install with: pip install questfoundry-py[openai]"
        )

    project_root = find_project_root(path)
    if not project_root:
        raise RuntimeError(
            "Not in a QuestFoundry project directory. "
            "Run 'qf init' to create a new project."
        )

    return WorkspaceManager(project_root)


def require_workspace(path: Optional[Path] = None) -> "WorkspaceManager":
    """
    Get WorkspaceManager or exit with error message.

    This is a convenience function for CLI commands that require
    a valid workspace. It provides user-friendly error messages
    and exits with code 1 on error.

    Args:
        path: Optional path to start search from (defaults to cwd)

    Returns:
        WorkspaceManager instance

    Note:
        This function calls sys.exit(1) on error, so it should only
        be used in CLI command contexts, not in library code.
    """
    import sys

    try:
        return get_workspace(path)
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def is_questfoundry_project(path: Optional[Path] = None) -> bool:
    """
    Check if the given path is in a QuestFoundry project.

    Args:
        path: Path to check (defaults to current working directory)

    Returns:
        True if in a QuestFoundry project, False otherwise
    """
    return find_project_root(path) is not None


def get_spec_path() -> Path:
    """
    Get the path to the questfoundry-spec directory.

    Checks in order:
    1. QUESTFOUNDRY_SPEC_PATH environment variable
    2. spec/ subdirectory relative to CLI package
    3. spec/ subdirectory in current working directory

    Returns:
        Path to spec directory

    Raises:
        RuntimeError: If spec directory cannot be found
    """
    import os

    # Check environment variable
    env_spec_path = os.getenv("QUESTFOUNDRY_SPEC_PATH")
    if env_spec_path:
        spec_path = Path(env_spec_path)
        if spec_path.exists() and spec_path.is_dir():
            return spec_path

    # Check relative to CLI package (for development/installed package)
    cli_root = Path(__file__).parent.parent.parent.parent
    spec_in_cli = cli_root / "spec"
    if spec_in_cli.exists() and spec_in_cli.is_dir():
        return spec_in_cli

    # Check in current working directory
    spec_in_cwd = Path.cwd() / "spec"
    if spec_in_cwd.exists() and spec_in_cwd.is_dir():
        return spec_in_cwd

    raise RuntimeError(
        "Could not find questfoundry-spec directory. "
        "Set QUESTFOUNDRY_SPEC_PATH environment variable or ensure "
        "spec/ submodule is initialized."
    )
