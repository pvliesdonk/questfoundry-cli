# Claude Code Instructions - QuestFoundry CLI

## Project Overview

QuestFoundry CLI (Layer 7) is a command-line interface for the QuestFoundry system. It provides user-friendly access to Layer 6 (questfoundry-py) library functionality.

## Core Structure

```
questfoundry-cli/
├── spec/                   # Submodule: questfoundry-spec
├── src/qf/                # Main package
│   ├── cli.py            # Main Typer app
│   ├── commands/         # Command implementations
│   ├── formatting/       # Rich text formatting
│   ├── interactive/      # Interactive mode
│   └── utils/            # Utilities
├── tests/                # Test suite
├── docs/                 # Documentation
├── pyproject.toml        # Project config
└── .claude/              # This directory
```

## Commit Standards

All commits must follow conventional commit format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Common Types

- `feat`: New feature (minor version bump)
- `fix`: Bug fix (patch version bump)
- `docs`: Documentation only
- `style`: Code formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Recommended Scopes

- `commands`: CLI command implementations
- `formatting`: Display/output formatting
- `interactive`: Interactive mode features
- `validation`: Validation features
- `config`: Configuration management
- `deps`: Dependencies
- `build`: Build/packaging

### Examples

```bash
feat(commands): implement qf init command
fix(formatting): correct table alignment issue
test(commands): add tests for qf list command
docs: update installation instructions
chore(deps): update typer to v0.9.1
```

## Branch Naming

Claude Code session branches must follow:

```
claude/<descriptive-name>-<session-id>
```

The session ID is in the system context - use it exactly as provided.

## Development Workflow

### Before Starting Work

1. **Sync environment**: `uv sync`
2. **Check current branch**: `git branch --show-current`
3. **Review implementation plan**: Check `spec/07-ui/IMPLEMENTATION_PLAN.md`
4. **Review updates**: Check `docs/LAYER_7_UPDATES_FOR_EPIC_7_8.md`

### During Development

1. **Validate changes**:
   ```bash
   uv run pytest          # Run tests
   uv run mypy src/       # Type checking
   uv run ruff check .    # Linting
   uv run ruff format .   # Formatting
   ```

2. **Commit with conventional format**:
   ```bash
   git add <files>
   git commit -m "feat(commands): add new command"
   ```

3. **Push with -u flag**:
   ```bash
   git push -u origin <branch-name>
   ```

## Coding Standards

- **Python version**: 3.11+
- **Line length**: 88 characters
- **Type hints**: Required on all functions
- **Docstrings**: Required on public APIs
- **Imports**: Ruff-sorted
- **Framework**: Typer for CLI, Rich for formatting

### CLI Patterns

```python
import typer
from rich.console import Console

app = typer.Typer(help="Command group description")
console = Console()

@app.command()
def command_name(
    arg: str = typer.Argument(..., help="Argument description"),
    option: str = typer.Option("default", "--option", "-o", help="Option description"),
):
    """Command description for help text."""
    try:
        # Implementation
        console.print("[green]✓ Success message[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
```

### Rich Formatting

```python
from rich.table import Table
from rich.panel import Panel

# Tables
table = Table(title="Title")
table.add_column("Column 1", style="cyan")
table.add_row("value")
console.print(table)

# Panels
panel = Panel("Content", title="Title")
console.print(panel)
```

## Testing

- Test files: `test_*.py`
- Test functions: `test_<function_name>`
- Target coverage: >80%
- Mirror source structure in tests/

### Example Test

```python
from typer.testing import CliRunner
from qf.cli import app

runner = CliRunner()

def test_command():
    result = runner.invoke(app, ["command", "arg"])
    assert result.exit_code == 0
    assert "expected" in result.stdout
```

## Epic Organization

Work is organized into epics (large features) and features (individual commits).

- Each epic gets its own branch
- Each feature is one commit
- Follow `epic-workflow.md` for details

## Helpful Commands

```bash
# Dependencies
uv sync                          # Install dependencies
uv add <package>                 # Add new dependency

# Testing
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose
uv run pytest --cov=src/qf       # With coverage

# Linting & Formatting
uv run ruff check .              # Check linting
uv run ruff check . --fix        # Auto-fix
uv run ruff format .             # Format code

# Type Checking
uv run mypy src/                 # Type check

# Pre-commit
pre-commit install               # Install hooks
pre-commit run --all-files       # Run all hooks
```

## Key Principles

1. **UX First**: CLI should be intuitive and beautiful
2. **Layer 6 Wrapper**: Business logic lives in Layer 6, not CLI
3. **Error Handling**: Always provide helpful error messages
4. **Progress Feedback**: Show progress for long operations
5. **Test Coverage**: All commands must have tests
6. **Type Safety**: Full type hints required
7. **Documentation**: Keep help text clear and useful

## Resources

- **Typer docs**: https://typer.tiangolo.com/
- **Rich docs**: https://rich.readthedocs.io/
- **QuestFoundry spec**: `spec/` directory
- **Implementation plan**: `spec/07-ui/IMPLEMENTATION_PLAN.md`
- **Architecture updates**: `docs/LAYER_7_UPDATES_FOR_EPIC_7_8.md`
