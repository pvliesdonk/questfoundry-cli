"""Interactive REPL shell for QuestFoundry commands"""


import typer
from rich.console import Console

from qf.utils import find_project_file

console = Console()


class QFShell:
    """Interactive shell for QuestFoundry commands"""

    def __init__(self, verbose: bool = False, use_history: bool = True):
        """Initialize shell session"""
        self.verbose = verbose
        self.use_history = use_history
        self.project_file = find_project_file()
        self.running = True
        self.commands_history: list[str] = []
        # Define available QuestFoundry commands (used in help and validation)
        self.qf_commands = [
            "list", "status", "show", "search", "diff", "run", "init", "version", "info"
        ]

    def welcome(self) -> None:
        """Display welcome message"""
        console.print()
        console.print("[bold cyan]QuestFoundry Interactive Shell[/bold cyan]")
        console.print("[dim]Type 'help' for available commands, 'exit' to quit[/dim]")
        if self.project_file:
            console.print(f"[dim]Project: {self.project_file.parent.name}[/dim]")
        console.print()

    def get_prompt(self) -> str:
        """Get shell prompt"""
        if self.project_file:
            project_name = self.project_file.parent.name
            return f"qf[{project_name}]> "
        return "qf> "

    def handle_help(self) -> None:
        """Show help for available commands"""
        console.print()
        console.print("[bold]Available Commands:[/bold]")
        console.print()

        commands = {
            "help": "Show this help message",
            "list": "List artifacts",
            "show <id>": "Show artifact details",
            "status": "Show project status",
            "init": "Initialize project",
            "search <query>": "Search artifacts",
            "diff <id>": "Show artifact diff",
            "run <loop>": "Run a loop",
            "history": "Show project history",
            "version": "Show version",
            "info": "Show QuestFoundry info",
            "exit/quit": "Exit shell",
        }

        max_len = max(len(cmd) for cmd in commands.keys())
        for cmd, description in commands.items():
            console.print(f"  [cyan]{cmd:<{max_len}}[/cyan]  {description}")

        console.print()

    def handle_history(self) -> None:
        """Show command history"""
        console.print()
        if not self.commands_history:
            console.print("[dim]No command history[/dim]")
        else:
            console.print("[bold]Command History:[/bold]")
            for i, cmd in enumerate(self.commands_history, 1):
                console.print(f"  {i:3d}  {cmd}")
        console.print()

    def run_command(self, command_line: str) -> bool:
        """Execute a shell command

        Returns:
            False if user wants to exit, True otherwise
        """
        # Add to history
        if self.use_history and command_line.strip():
            self.commands_history.append(command_line)

        # Parse command
        parts = command_line.strip().split(None, 1)
        if not parts:
            return True

        command = parts[0].lower()

        # Handle built-in shell commands
        if command in ["exit", "quit", "q"]:
            console.print("[dim]Exiting shell...[/dim]")
            return False

        if command == "help":
            self.handle_help()
            return True

        if command == "history":
            self.handle_history()
            return True

        if command == "clear":
            console.clear()
            return True

        # Try to execute as QuestFoundry command
        # For now, show a placeholder message
        if command in self.qf_commands:
            # Map shell command to qf command
            console.print(
                f"[dim]Command '{command}' would be executed as "
                f"'qf {command_line}'[/dim]"
            )
            # In a real implementation, this would import and execute the command
            return True

        # Unknown command
        if command:
            console.print(
                f"[yellow]Unknown command: {command}[/yellow] "
                f"[dim](type 'help' for available commands)[/dim]"
            )

        return True

    def run(self) -> None:
        """Run interactive shell loop"""
        self.welcome()

        try:
            while self.running:
                try:
                    prompt = self.get_prompt()
                    user_input = input(prompt)
                    if not self.run_command(user_input):
                        break
                except KeyboardInterrupt:
                    console.print()
                    console.print("[dim]Use 'exit' or 'quit' to exit[/dim]")
                except EOFError:
                    # Ctrl+D
                    console.print()
                    break
        except Exception as e:
            if self.verbose:
                console.print(f"[red]Error: {e}[/red]")
            else:
                console.print("[red]Shell error - use --verbose for details[/red]")

        console.print("[dim]Shell closed[/dim]\n")


def shell_command(
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    no_history: bool = typer.Option(
        False, "--no-history", help="Disable command history"
    ),
) -> None:
    """Start interactive QuestFoundry shell

    The interactive shell allows you to run QuestFoundry commands without
    the 'qf' prefix. Project context is maintained between commands.

    Examples:
        qf shell              # Start interactive shell
        qf shell --verbose    # Start with verbose output
    """
    # Check project exists (optional warning)
    project_file = find_project_file()
    if not project_file:
        console.print(
            "[yellow]Warning: No project found in current directory[/yellow]"
        )
        console.print(
            "[cyan]You can still explore QuestFoundry, but project commands "
            "won't work[/cyan]"
        )
        console.print()

    # Create and run shell
    shell = QFShell(verbose=verbose, use_history=not no_history)
    shell.run()
