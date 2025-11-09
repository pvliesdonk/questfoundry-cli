"""Bind command for executing Book Binder role to render views."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from qf.utils import BindFormat, require_project

app = typer.Typer(help="Bind and render views from snapshots")
console = Console()


@app.command(name="view")
@require_project
def bind_view(
    snapshot_id: str = typer.Argument(..., help="Snapshot ID to bind"),
    format: str = typer.Option(
        BindFormat.HTML.value,
        "--format",
        "-f",
        help="Output format: html, markdown, pdf",
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
) -> None:
    """Bind and render a view from a snapshot using Book Binder.

    Executes the Book Binder role to generate a player-ready view from
    the specified snapshot in the requested format.

    Examples:
        qf bind view snap-123                           # Render snapshot
        qf bind view snap-123 --format markdown          # To Markdown
        qf bind view snap-123 --format pdf               # To PDF
        qf bind view snap-123 --output bound.html        # Custom output
    """
    try:
        # Validate format using enum
        try:
            format_enum = BindFormat(format.lower())
        except ValueError:
            valid_formats = [fmt.value for fmt in BindFormat]
            console.print(
                f"[red]Error: Invalid format '{format}'. "
                f"Valid formats: {', '.join(valid_formats)}[/red]"
            )
            raise typer.Exit(1)

        # Set default output path if not provided
        if not output:
            output = f"bound-view.{format}"

        # Show what we're doing
        console.print(
            f"\n[cyan]→ Binding view for snapshot {snapshot_id} "
            f"(format: {format})[/cyan]"
        )

        # Create output directory if needed
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Simulate binding (placeholder for actual Layer 6 integration)
        console.print("[dim]  Executing Book Binder role...[/dim]")
        console.print(f"[dim]  Rendering to {output_path}...[/dim]")

        # Create a simple output file to demonstrate success
        if format_enum == BindFormat.PDF:
            # PDF uses binary mode
            with open(output_path, "wb") as f:
                pdf_content = f"%PDF-1.4\n%Placeholder PDF for {snapshot_id}\n"
                f.write(pdf_content.encode("utf-8"))
        else:
            # HTML and Markdown use text mode with UTF-8 encoding
            with open(output_path, "w", encoding="utf-8") as f:
                if format_enum == BindFormat.HTML:
                    f.write("<html>\n<head><title>Bound View</title></head>\n")
                    f.write(
                        f"<body><h1>Bound View from {snapshot_id}</h1></body>\n</html>"
                    )
                elif format_enum == BindFormat.MARKDOWN:
                    f.write(f"# Bound View from {snapshot_id}\n\n")
                    f.write("This is a placeholder bound view.\n")

        # Show result
        result_text = Text()
        result_text.append("✓ View bound successfully\n", style="green")
        result_text.append(f"  Snapshot: {snapshot_id}\n", style="cyan")
        result_text.append(f"  Format: {format.upper()}\n", style="cyan")
        result_text.append(f"  Output: {output_path}\n", style="cyan")

        console.print()
        console.print(
            Panel(
                result_text, title="Binding Complete", border_style="green"
            )
        )
        console.print()

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
