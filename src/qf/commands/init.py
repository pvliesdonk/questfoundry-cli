"""Project initialization command"""

import json
import os
from pathlib import Path
from typing import Optional

import questionary
import typer
from rich.console import Console
from rich.panel import Panel

from ..utils.formatting import print_header, print_success
from ..utils.workspace import get_workspace, QUESTFOUNDRY_AVAILABLE

console = Console()


def get_author_name() -> str:
    """Get author name from git config or environment"""
    # Try git config first
    try:
        import subprocess
        result = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Try environment variables
    for env_var in ["USER", "USERNAME", "LOGNAME"]:
        if value := os.getenv(env_var):
            return value

    return "unknown"


def create_project_structure(
    project_path: Path,
    project_name: str,
    description: str,
    author: Optional[str] = None,
    version: str = "0.1.0",
) -> None:
    """Create project directory structure using WorkspaceManager"""
    if QUESTFOUNDRY_AVAILABLE:
        # Use questfoundry-py WorkspaceManager for proper SQLite database initialization
        from questfoundry.state import WorkspaceManager

        ws = WorkspaceManager(project_path)
        ws.init_workspace(
            name=project_name,
            description=description,
            version=version,
            author=author or get_author_name(),
        )

        # Copy config template if it doesn't exist
        config_file = project_path / ".questfoundry" / "config.yml"
        if not config_file.exists():
            template_path = Path(__file__).parent.parent / "templates" / "config.yml"
            if template_path.exists():
                with open(template_path) as template:
                    config_content = template.read()
                with open(config_file, "w") as f:
                    f.write(config_content)

    else:
        # Fallback: Legacy directory structure without database
        console.print(
            "[yellow]Warning: questfoundry-py not installed. "
            "Creating basic structure without database.[/yellow]\n"
        )

        # Create .questfoundry workspace
        workspace = project_path / ".questfoundry"
        workspace.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (workspace / "hot").mkdir(exist_ok=True)
        (workspace / "hot" / "hooks").mkdir(exist_ok=True)
        (workspace / "hot" / "canon").mkdir(exist_ok=True)
        (workspace / "hot" / "artifacts").mkdir(exist_ok=True)
        (workspace / "cache").mkdir(exist_ok=True)
        (workspace / "sessions").mkdir(exist_ok=True)

        # Create legacy JSON metadata file
        project_file = project_path / f"{project_name}.qfproj"
        metadata = {
            "name": project_name,
            "description": description,
            "version": version,
            "author": author or get_author_name(),
            "layers": {
                "hot": str(workspace / "hot"),
                "cold": str(project_file),
            },
        }

        with open(project_file, "w") as f:
            json.dump(metadata, f, indent=2)

        # Create default config from template
        config_file = workspace / "config.yml"
        template_path = Path(__file__).parent.parent / "templates" / "config.yml"

        if template_path.exists():
            with open(template_path) as template:
                config_content = template.read()
            with open(config_file, "w") as f:
                f.write(config_content)


def init_command(
    path: Optional[str] = typer.Argument(None, help="Project directory path"),
) -> None:
    """Initialize a new QuestFoundry project"""

    # Determine project path
    if path:
        project_path = Path(path).resolve()
    else:
        project_path = Path.cwd()

    # Check if directory exists and is empty
    if project_path.exists():
        if not project_path.is_dir():
            console.print(f"[red]Error: {project_path} is not a directory[/red]")
            raise typer.Exit(1)

        # Check if already initialized
        if (project_path / ".questfoundry").exists():
            console.print(f"[red]Error: Project already exists in {project_path}[/red]")
            console.print(
                "[yellow]Tip: Use 'qf status' to see project information[/yellow]"
            )
            raise typer.Exit(1)
    else:
        project_path.mkdir(parents=True, exist_ok=True)

    # Prompt for project metadata
    print_header("Initialize QuestFoundry Project")

    console.print("Setting up your new project...\n")

    # Get project name (default to directory name)
    default_name = project_path.name
    project_name = questionary.text(
        "Project name:",
        default=default_name,
        validate=lambda x: len(x) > 0 or "Project name cannot be empty",
    ).ask()

    if not project_name:
        console.print("[yellow]Initialization cancelled[/yellow]")
        raise typer.Exit(0)

    # Get description
    description = questionary.text(
        "Description (optional):",
        default="",
    ).ask()

    if description is None:
        console.print("[yellow]Initialization cancelled[/yellow]")
        raise typer.Exit(0)

    # Create project structure
    try:
        create_project_structure(project_path, project_name, description)

        # Success message
        console.print()
        print_success("Project initialized successfully!")
        console.print()

        # Show what was created
        if QUESTFOUNDRY_AVAILABLE:
            database_info = "[cyan]Database:[/cyan] project.qfproj (SQLite)\n"
        else:
            database_info = f"[cyan]Metadata:[/cyan] {project_name}.qfproj (JSON)\n"

        panel_content = f"""[cyan]Project:[/cyan] {project_name}
[cyan]Location:[/cyan] {project_path}
{database_info}[cyan]Workspace:[/cyan] .questfoundry/hot/

[bold]Next steps:[/bold]
  1. Run [green]qf status[/green] to see project information
  2. Run [green]qf schema list[/green] to see available schemas
  3. Check out the documentation at:
     https://github.com/pvliesdonk/questfoundry-spec
"""

        console.print(
            Panel(panel_content, title="✨ Project Created", border_style="green")
        )

    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        raise typer.Exit(1)
