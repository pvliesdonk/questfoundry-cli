"""Project utility functions"""

import json
from pathlib import Path
from typing import Any

# Standard artifact types in QuestFoundry workspace
ARTIFACT_TYPES = ["hooks", "canon", "codex", "tus", "artifacts"]


def find_project_file() -> Path | None:
    """Find .qfproj file in current directory"""
    project_files = list(Path.cwd().glob("*.qfproj"))
    if project_files:
        return project_files[0]
    return None


def load_project_metadata(project_file: Path) -> Any:
    """Load project metadata from .qfproj file"""
    with open(project_file, encoding="utf-8") as f:
        return json.load(f)
