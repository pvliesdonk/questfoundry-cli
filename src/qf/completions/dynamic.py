"""Dynamic completion functions for shell completion support."""

from typing import List, Optional

from click import Context, Parameter


def complete_artifact_ids(
    ctx: Optional[Context] = None,
    param: Optional[Parameter] = None,
    incomplete: str = "",
) -> List[str]:
    """Complete artifact IDs from the current project.

    Args:
        incomplete: Partial artifact ID being completed

    Returns:
        List of completion items for matching artifact IDs
    """
    from qf.utils import find_project_file, load_project_metadata

    completions: List[str] = []

    # Find project file
    project_file = find_project_file()
    if not project_file:
        return completions

    try:
        # Load project metadata
        metadata = load_project_metadata(project_file)

        # Get artifact IDs from project (if available)
        # This is a placeholder - actual structure depends on project format
        artifacts = metadata.get("artifacts", [])
        if isinstance(artifacts, dict):
            artifact_ids = list(artifacts.keys())
        elif isinstance(artifacts, list):
            artifact_ids = artifacts
        else:
            artifact_ids = []

        # Filter by incomplete prefix
        for artifact_id in artifact_ids:
            if artifact_id.startswith(incomplete):
                completions.append(artifact_id)

        # Always include common artifact ID patterns
        patterns = [
            "snap-001",
            "snap-002",
            "snap-latest",
            "artifact-001",
        ]
        for pattern in patterns:
            if pattern.startswith(incomplete):
                completions.append(pattern)

        return completions
    except Exception:
        # Return empty list on any error
        return completions


def complete_loop_names(
    ctx: Optional[Context] = None,
    param: Optional[Parameter] = None,
    incomplete: str = "",
) -> List[str]:
    """Complete loop names available in the current project.

    Args:
        incomplete: Partial loop name being completed

    Returns:
        List of completion items for matching loop names
    """
    from qf.utils import find_project_file, load_project_metadata

    completions: List[str] = []

    # Find project file
    project_file = find_project_file()
    if not project_file:
        return completions

    try:
        # Load project metadata
        metadata = load_project_metadata(project_file)

        # Get loop names from project (if available)
        loops = metadata.get("loops", [])
        if isinstance(loops, dict):
            loop_names = list(loops.keys())
        elif isinstance(loops, list):
            loop_names = loops
        else:
            loop_names = []

        # Filter by incomplete prefix
        for loop_name in loop_names:
            if loop_name.startswith(incomplete):
                completions.append(loop_name)

        return completions
    except Exception:
        # Return empty list on any error
        return completions


def complete_provider_names(
    ctx: Optional[Context] = None,
    param: Optional[Parameter] = None,
    incomplete: str = "",
) -> List[str]:
    """Complete provider names available in the system.

    Args:
        incomplete: Partial provider name being completed

    Returns:
        List of completion items for matching provider names
    """
    completions: List[str] = []

    # Standard providers available in QuestFoundry
    # These are the default providers that should be available
    standard_providers = [
        "openai",
        "anthropic",
        "groq",
        "ollama",
        "local",
        "mock",
        "test",
    ]

    # Filter by incomplete prefix
    for provider in standard_providers:
        if provider.startswith(incomplete.lower()):
            completions.append(provider)

    # Add custom providers if any exist
    try:
        from qf.utils import find_project_file, load_project_metadata

        project_file = find_project_file()
        if project_file:
            metadata = load_project_metadata(project_file)
            custom_providers = metadata.get("providers", {})
            if isinstance(custom_providers, dict):
                for provider_name in custom_providers.keys():
                    if provider_name.startswith(incomplete.lower()):
                        completions.append(provider_name)
    except Exception:
        # Ignore errors when loading custom providers
        pass

    return completions
