"""Loop execution commands"""

import asyncio
import logging
import os
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from questfoundry.orchestration import Showrunner
from questfoundry.state import WorkspaceManager

console = Console()
logger = logging.getLogger(__name__)


def _load_loops() -> dict[str, dict[str, str]]:
    """Load loop definitions from YAML configuration file."""
    loops_file = Path(__file__).parent.parent / "data" / "loops.yml"
    with open(loops_file, "r", encoding="utf-8") as f:
        loops = yaml.safe_load(f)
        return loops if loops is not None else {}


# All 13 loops from Layer 2 spec (02-dictionary/loop_names.md)
LOOPS = _load_loops()


def get_loop_help() -> str:
    """Generate help text listing all available loops by category"""
    help_text = "Name of the loop to execute (use 'qf loops' to see all available loops)"
    return help_text


def display_loops_list() -> None:
    """Display all available loops organized by category"""
    console.print()
    console.print("[bold cyan]Available QuestFoundry Loops[/bold cyan]\n")

    # Group loops by category
    categories: dict[str, list[tuple[str, dict]]] = {}
    for loop_id, loop_info in LOOPS.items():
        category = loop_info.get("category", "Other")
        if category not in categories:
            categories[category] = []
        categories[category].append((loop_id, loop_info))

    # Display by category
    for category in ["Discovery", "Refinement", "Asset", "Export"]:
        if category in categories:
            console.print(f"[bold magenta]{category}:[/bold magenta]")
            for loop_id, loop_info in sorted(categories[category]):
                display_name = loop_info["display_name"]
                abbrev = loop_info.get("abbrev", "")
                desc = loop_info["description"]
                console.print(f"  [cyan]{loop_id:20}[/cyan] ({abbrev}) - {desc}")
            console.print()

    console.print("[dim]Run a loop with:[/dim] [green]qf run <loop-name>[/green]\n")


def validate_loop_name(loop_name: str) -> str:
    """
    Validate and normalize loop name.

    Args:
        loop_name: Loop name to validate (kebab-case or display name)

    Returns:
        Normalized kebab-case loop name

    Raises:
        typer.Exit: If loop name is invalid
    """
    # normalize to lowercase and replace spaces with hyphens
    normalized = loop_name.lower().strip().replace(" ", "-")

    # check if it's a valid loop name
    if normalized in LOOPS:
        return normalized

    # check if it matches any display name (case-insensitive)
    for loop_id, loop_info in LOOPS.items():
        display_name = str(loop_info["display_name"])
        if display_name.lower() == loop_name.lower():
            return loop_id

    # invalid loop name
    console.print(f"[red]Error: Unknown loop '{loop_name}'[/red]")
    console.print("\n[cyan]Available loops:[/cyan]")
    for loop_id, loop_info in LOOPS.items():
        console.print(
            f"  • {loop_info['display_name']} ({loop_id}) - {loop_info['description']}"
        )
    raise typer.Exit(1)


def validate_story_spark_seed() -> str | None:
    """
    Validate that a seed is available for story-spark loop.

    Returns:
        Seed text if available, None if not configured
    """
    # Check for seed in environment variable or config
    seed = os.environ.get("QUESTFOUNDRY_SEED")
    if seed:
        return seed

    # Check for seed file in workspace
    seed_file = Path(".questfoundry") / "seed.txt"
    if seed_file.exists():
        with open(seed_file, encoding="utf-8") as f:
            return f.read().strip()

    return None


def run(
    loop_name: str = typer.Argument(..., help=get_loop_help()),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Enable interactive mode (coming soon)"
    ),
) -> None:
    """Execute a loop"""
    # Run async execution in sync context
    asyncio.run(_run_async(loop_name, interactive))


async def _run_async(loop_name: str, interactive: bool) -> None:
    """Async loop execution"""
    # check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # validate loop name
    logger.debug(f"Validating loop name: {loop_name}")
    loop_id = validate_loop_name(loop_name)
    loop_info = LOOPS[loop_id]
    logger.info(f"Executing loop: {loop_id} ({loop_info['display_name']})")

    # check workspace exists
    workspace = Path(WORKSPACE_DIR)
    if not workspace.exists():
        console.print("[red]Error: Workspace not found[/red]")
        raise typer.Exit(1)

    logger.debug(f"Workspace found at: {workspace.absolute()}")

    # Special handling for story-spark: check for seed in config or environment
    if loop_id == "story-spark":
        story_seed = validate_story_spark_seed()
        if not story_seed:
            logger.warning("Story Spark requires a seed but none was found")
            console.print(
                "[yellow]⚠ Story Spark requires a seed[/yellow]"
            )
            console.print(
                "  A seed is a prompt or concept to generate story ideas from."
            )
            console.print(
                "  Set the seed in your project config:"
            )
            console.print(
                "    [green]qf config set story_seed 'Your story concept'[/green]"
            )
            console.print(
                "  Or set an environment variable:"
            )
            console.print(
                "    [green]export QUESTFOUNDRY_SEED='Your story concept'[/green]\n"
            )
            raise typer.Exit(1)
        logger.debug(f"Story Spark seed found (length: {len(story_seed)} chars)")

    # show warning for interactive mode
    if interactive:
        console.print(
            "[yellow]Note: Interactive mode will be available "
            "in a future release.[/yellow]\n"
        )

    # Display loop and roles prominently
    console.print()
    console.print(
        Panel(
            f"[bold cyan]{loop_info['display_name']}[/bold cyan]\n"
            f"[dim]{loop_info['description']}[/dim]",
            title=f"Loop Execution - {loop_info['abbrev']}",
            border_style="cyan",
        )
    )

    # Show loop category and display active roles for this loop
    category = loop_info.get("category", "Unknown")
    console.print(f"\n[bold]Category:[/bold] {category}\n")

    logger.info("Starting loop execution")
    console.print("[dim]Executing loop with questfoundry-py...[/dim]\n")

    # Execute the loop using questfoundry-py Showrunner
    try:
        logger.debug("Executing loop with questfoundry-py Showrunner")
        await execute_loop_with_showrunner(
            loop_id, loop_info, workspace, project_file
        )
    except Exception as e:
        logger.error(f"Error executing loop: {e}")
        console.print(f"[red]Error executing loop:[/red] {e}\n")
        raise typer.Exit(1)


async def execute_loop_with_showrunner(
    loop_id: str, loop_info: dict, workspace: Path, project_file: Path
) -> None:
    """Execute a loop using questfoundry-py Showrunner"""
    logger.debug(f"Initializing WorkspaceManager from {workspace}")
    ws = WorkspaceManager(workspace.parent)

    # Get seed if this is story-spark
    seed = None
    if loop_id == "story-spark":
        seed = validate_story_spark_seed()
        logger.debug(f"Story Spark seed: {seed[:50] if seed else 'None'}...")

    logger.debug(f"Creating Showrunner for loop: {loop_id}")
    showrunner = Showrunner(workspace=ws)

    logger.info(f"Executing loop {loop_id} with Showrunner")

    # Execute loop with seed if available
    try:
        if seed and loop_id == "story-spark":
            logger.debug("Executing story-spark with seed")
            result = await showrunner.run_loop(loop_id, seed=seed)
        else:
            result = await showrunner.run_loop(loop_id)
    except TypeError:
        # Fallback if seed parameter is not supported
        logger.debug("Seed parameter not supported, executing without seed")
        result = await showrunner.run_loop(loop_id)

    logger.info(f"Loop execution completed: {loop_id}")
    console.print(f"[green]✓ Loop execution completed[/green]")

    if result:
        console.print(f"\n[bold]Results:[/bold]")
        console.print(result)
