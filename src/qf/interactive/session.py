"""Quickstart session management and state tracking."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()


class QuickstartSession:
    """Manages state and progress during quickstart workflow.

    Attributes:
        project_name: Name of the project being set up
        project_file: Path to .qfproj file
        premise: Story premise
        tone: Selected story tone
        length: Selected story length
        completed_loops: List of completed loop names
        current_loop: Currently executing loop name
        interactive_mode: Whether interactive mode is enabled
    """

    def __init__(self) -> None:
        """Initialize quickstart session."""
        self.project_name: str = ""
        self.project_file: Optional[Path] = None
        self.workspace_dir: Optional[Path] = None
        self.premise: str = ""
        self.tone: str = ""
        self.length: str = ""
        self.completed_loops: list[str] = []
        self.current_loop: Optional[str] = None
        self.interactive_mode: bool = False
        self.start_time: datetime = datetime.now()

    def create_project(self, name: str, premise: str, tone: str, length: str) -> bool:
        """Create a new QuestFoundry project.

        Args:
            name: Project name
            premise: Story premise
            tone: Story tone/genre
            length: Story length

        Returns:
            True if project created successfully, False otherwise
        """
        try:
            self.project_name = name
            self.premise = premise
            self.tone = tone
            self.length = length

            # Create project file (.qfproj)
            project_file = Path(f"{name}.qfproj")
            workspace_dir = Path(".questfoundry")

            # Create workspace directory
            workspace_dir.mkdir(exist_ok=True)

            # Create subdirectories
            (workspace_dir / "hot").mkdir(exist_ok=True)
            (workspace_dir / "cold").mkdir(exist_ok=True)
            (workspace_dir / "assets").mkdir(exist_ok=True)
            (workspace_dir / "assets" / "images").mkdir(exist_ok=True)
            (workspace_dir / "assets" / "audio").mkdir(exist_ok=True)

            # Create project metadata file
            metadata = {
                "name": name,
                "premise": premise,
                "tone": tone,
                "length": length,
                "created": datetime.now().isoformat(),
            }

            metadata_file = workspace_dir / "project.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))

            self.project_file = project_file
            self.workspace_dir = workspace_dir

            console.print(f"[green]✓[/green] Project created: {project_file}")
            return True

        except Exception as e:
            console.print(f"[red]Error creating project: {e}[/red]")
            return False

    def start_loop(self, loop_name: str) -> None:
        """Mark loop as started.

        Args:
            loop_name: Name of loop being executed
        """
        self.current_loop = loop_name

    def complete_loop(self, loop_name: str) -> None:
        """Mark loop as completed.

        Args:
            loop_name: Name of loop that was completed
        """
        if loop_name not in self.completed_loops:
            self.completed_loops.append(loop_name)
        self.current_loop = None

    def save_checkpoint(self) -> None:
        """Save session state for potential resumption.

        Saves current session data to a checkpoint file in workspace.
        """
        if not self.workspace_dir:
            return

        checkpoint = {
            "project_name": self.project_name,
            "premise": self.premise,
            "tone": self.tone,
            "length": self.length,
            "completed_loops": self.completed_loops,
            "current_loop": self.current_loop,
            "interactive_mode": self.interactive_mode,
            "saved_at": datetime.now().isoformat(),
        }

        checkpoint_file = self.workspace_dir / ".quickstart_checkpoint.json"
        checkpoint_file.write_text(json.dumps(checkpoint, indent=2))

    def load_checkpoint(self) -> bool:
        """Load session state from checkpoint.

        Returns:
            True if checkpoint loaded successfully, False if no checkpoint found
        """
        checkpoint_file = Path(".questfoundry") / ".quickstart_checkpoint.json"

        if not checkpoint_file.exists():
            return False

        try:
            checkpoint = json.loads(checkpoint_file.read_text())

            self.project_name = checkpoint.get("project_name", "")
            self.premise = checkpoint.get("premise", "")
            self.tone = checkpoint.get("tone", "")
            self.length = checkpoint.get("length", "")
            self.completed_loops = checkpoint.get("completed_loops", [])
            self.current_loop = checkpoint.get("current_loop")
            self.interactive_mode = checkpoint.get("interactive_mode", False)
            self.workspace_dir = Path(".questfoundry")

            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load checkpoint: {e}[/yellow]")
            return False

    def can_resume(self) -> bool:
        """Check if session can be resumed from checkpoint.

        Returns:
            True if checkpoint exists and is valid, False otherwise
        """
        checkpoint_file = Path(".questfoundry") / ".quickstart_checkpoint.json"
        return checkpoint_file.exists()

    def get_session_status(self) -> dict[str, Any]:
        """Get current session status.

        Returns:
            Dictionary with session information
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"

        return {
            "project_name": self.project_name,
            "premise": self.premise,
            "tone": self.tone,
            "length": self.length,
            "completed_loops": self.completed_loops,
            "current_loop": self.current_loop,
            "elapsed_time": elapsed_str,
            "interactive_mode": self.interactive_mode,
        }

    def enable_interactive_mode(self) -> None:
        """Enable interactive mode for agent collaboration."""
        self.interactive_mode = True

    def disable_interactive_mode(self) -> None:
        """Disable interactive mode."""
        self.interactive_mode = False
