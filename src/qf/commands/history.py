"""Project history command"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()


def find_project_file() -> Path | None:
    """Find .qfproj file in current directory"""
    project_files = list(Path.cwd().glob("*.qfproj"))
    if project_files:
        return project_files[0]
    return None


def history_command(
    tree_view: bool = typer.Option(False, "--tree", "-t", help="Display as tree"),
) -> None:
    """Show project history and TU timeline"""

    # Find project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    workspace = Path(".questfoundry")
    if not workspace.exists():
        console.print("[red]Error: Workspace not found[/red]")
        raise typer.Exit(1)

    # Look for TU briefs
    tus_path = workspace / "hot" / "tus"
    if not tus_path.exists() or not list(tus_path.glob("*.json")):
        console.print(
            "\n[dim]No history yet. TUs will appear here once loops execute.[/dim]\n"
        )
        return

    # Load TUs
    tus = []
    for tu_file in sorted(tus_path.glob("*.json")):
        try:
            with open(tu_file) as f:
                data = json.load(f)
                tus.append(
                    {
                        "id": data.get("id", tu_file.stem),
                        "title": data.get("title", "Untitled"),
                        "status": data.get("status", "unknown"),
                        "loops": data.get("loops", []),
                        "file": tu_file.name,
                    }
                )
        except (json.JSONDecodeError, KeyError):
            continue

    if not tus:
        console.print("\n[dim]No valid TUs found.[/dim]\n")
        return

    # Display as tree or table
    if tree_view:
        console.print("\n[bold cyan]TU Timeline (Tree View)[/bold cyan]\n")
        tree = Tree("📚 Project TUs")

        for tu in tus:
            tu_node = tree.add(
                f"[cyan]{tu['id']}:[/cyan] {tu['title']} [{tu['status']}]"
            )

            if tu["loops"]:
                loops_node = tu_node.add("Loops:")
                for loop in tu["loops"]:
                    loops_node.add(f"• {loop}")
            else:
                tu_node.add("[dim]No loops recorded[/dim]")

        console.print(tree)
    else:
        console.print("\n[bold cyan]TU Timeline[/bold cyan]\n")
        table = Table()
        table.add_column("TU ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Status", style="green")
        table.add_column("Loops", style="magenta")

        for tu in tus:
            loops_display = ", ".join(tu["loops"]) if tu["loops"] else "[dim]none[/dim]"
            table.add_row(
                tu["id"],
                tu["title"],
                tu["status"],
                loops_display,
            )

        console.print(table)

    console.print()
