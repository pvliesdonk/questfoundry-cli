# QuestFoundry CLI - Implementation Plan V2

**Based on:** NEW_CLI_DESIGN.md (reality-based approach)
**Timeline:** 7 days
**Approach:** Build on actual questfoundry-py v0.5.0, not outdated specs

---

## Overview

This is a **complete rewrite** of the CLI based on understanding the actual system:
- QuestFoundry = AI-powered gamebook authoring with 15 specialized roles
- questfoundry-py provides Orchestrator, WorkspaceManager, LoopRegistry, etc.
- CLI = thin wrapper exposing library functionality to users

---

## Phase 1: Foundation (Day 1)

### Goal
Basic project management without AI calls. Prove WorkspaceManager integration works.

### Tasks

#### 1.1: Clean Slate

```bash
# Archive old implementation
mv src/qf/commands src/qf/commands_old
mv src/qf/data src/qf/data_old

# Create new structure
mkdir -p src/qf/commands
mkdir -p src/qf/utils
mkdir -p src/qf/formatting
touch src/qf/commands/__init__.py
```

#### 1.2: Workspace Utilities

**File:** `src/qf/utils/workspace.py` (~30 lines)

```python
"""Workspace discovery utilities."""
from pathlib import Path
from questfoundry.state import WorkspaceManager

def find_workspace() -> Path:
    """Find .questfoundry workspace in current or parent directories."""
    current = Path.cwd()
    while current != current.parent:
        workspace = current / ".questfoundry"
        if workspace.exists() and workspace.is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("No QuestFoundry workspace found")

def get_workspace_manager() -> WorkspaceManager:
    """Get WorkspaceManager for current workspace."""
    workspace_path = find_workspace()
    return WorkspaceManager(workspace_path)
```

#### 1.3: Initialize Command

**File:** `src/qf/commands/init.py` (~80 lines)

```python
"""Project initialization command."""
from pathlib import Path
import typer
from rich.console import Console
from questfoundry.state import WorkspaceManager

console = Console()

def init(
    path: Path = typer.Argument(Path.cwd(), help="Project directory"),
    name: str = typer.Option(None, "--name", help="Project name"),
    author: str = typer.Option(None, "--author", help="Author name"),
    description: str = typer.Option("", "--description", help="Project description"),
) -> None:
    """Initialize a new QuestFoundry project."""

    # Check if project already exists
    workspace_dir = path / ".questfoundry"
    if workspace_dir.exists():
        console.print(f"[red]Error: Project already exists at {path}[/red]")
        raise typer.Exit(1)

    # Prompt for missing info
    if not name:
        name = typer.prompt("Project name", default=path.name)

    if not author:
        author = typer.prompt("Author name", default="")

    # Initialize workspace using library
    console.print(f"\n[cyan]Initializing project: {name}[/cyan]")

    ws = WorkspaceManager(path)
    ws.init_workspace(name=name, author=author, description=description)

    console.print(f"[green]✓ Project initialized at {path}[/green]")
    console.print(f"\n[cyan]Workspace structure:[/cyan]")
    console.print(f"  {workspace_dir}/")
    console.print(f"    hot/          [dim]# Work-in-progress artifacts[/dim]")
    console.print(f"    config.yml    [dim]# Provider configuration[/dim]")
    console.print(f"  {path.name}.qfproj  [dim]# Cold storage (SQLite)[/dim]")

    console.print(f"\n[cyan]Next steps:[/cyan]")
    console.print(f"  cd {path}")
    console.print(f"  qf config set providers.text.default openai")
    console.print(f"  qf config set providers.text.openai.api_key YOUR_KEY")
    console.print(f"  qf loop run hook-harvest")
```

#### 1.4: Status Command

**File:** `src/qf/commands/status.py` (~60 lines)

```python
"""Project status command."""
import typer
from rich.console import Console
from rich.table import Table
from questfoundry.state import WorkspaceManager
from ..utils.workspace import get_workspace_manager

console = Console()

def status() -> None:
    """Show project status."""

    try:
        ws = get_workspace_manager()
    except FileNotFoundError:
        console.print("[red]No QuestFoundry project found[/red]")
        console.print("[cyan]Run 'qf init' to create a project[/cyan]")
        raise typer.Exit(1)

    # Get project info
    info = ws.get_project_info()

    console.print(f"\n[cyan]Project:[/cyan] {info.name}")
    if info.author:
        console.print(f"[cyan]Author:[/cyan] {info.author}")
    if info.description:
        console.print(f"[cyan]Description:[/cyan] {info.description}")

    # Hot artifacts
    hot_artifacts = ws.list_hot_artifacts()
    console.print(f"\n[cyan]Hot artifacts:[/cyan] {len(hot_artifacts)}")

    # Group by type
    by_type = {}
    for art in hot_artifacts:
        by_type.setdefault(art.type, 0)
        by_type[art.type] += 1

    if by_type:
        table = Table(show_header=True)
        table.add_column("Type")
        table.add_column("Count", justify="right")
        for type_name, count in sorted(by_type.items()):
            table.add_row(type_name, str(count))
        console.print(table)

    # Cold artifacts
    cold_artifacts = ws.list_cold_artifacts()
    if cold_artifacts:
        console.print(f"\n[cyan]Cold artifacts:[/cyan] {len(cold_artifacts)}")

    # TUs
    tus = ws.list_tus()
    if tus:
        console.print(f"[cyan]Time units:[/cyan] {len(tus)}")
        console.print(f"  Latest: {tus[-1].id}")
```

#### 1.5: Config Command

**File:** `src/qf/commands/config.py` (~100 lines)

```python
"""Configuration management command."""
from pathlib import Path
import yaml
import typer
from rich.console import Console
from ..utils.workspace import find_workspace

console = Console()

def get_config_path() -> Path:
    """Get path to config.yml."""
    workspace = find_workspace()
    return workspace / ".questfoundry" / "config.yml"

def load_config() -> dict:
    """Load config file."""
    config_path = get_config_path()
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}

def save_config(config: dict) -> None:
    """Save config file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

def get(key: str) -> None:
    """Get configuration value."""
    config = load_config()

    # Navigate nested keys (e.g., "providers.text.default")
    value = config
    for part in key.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            console.print(f"[red]Key not found: {key}[/red]")
            raise typer.Exit(1)

    console.print(f"{key}: {value}")

def set(key: str, value: str) -> None:
    """Set configuration value."""
    config = load_config()

    # Navigate nested keys and set value
    parts = key.split(".")
    current = config
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value
    save_config(config)

    console.print(f"[green]✓ Set {key} = {value}[/green]")

def list_config() -> None:
    """List all configuration."""
    config = load_config()

    def print_dict(d, prefix=""):
        for key, value in sorted(d.items()):
            if isinstance(value, dict):
                print_dict(value, prefix=f"{prefix}{key}.")
            else:
                # Mask API keys
                if "key" in key.lower() or "secret" in key.lower():
                    value = "***"
                console.print(f"{prefix}{key}: {value}")

    if config:
        print_dict(config)
    else:
        console.print("[dim]No configuration set[/dim]")
```

### Deliverable

- [ ] `qf init` works - creates real workspace
- [ ] `qf status` works - shows project info
- [ ] `qf config get/set/list` works - manages config.yml
- [ ] No AI calls yet
- [ ] ~200 lines total

---

## Phase 2: Loop Execution (Days 2-3)

### Goal
**THE CRITICAL FEATURE** - Real loop execution via Orchestrator

### Tasks

#### 2.1: Provider Setup Utilities

**File:** `src/qf/utils/providers.py` (~50 lines)

```python
"""Provider utilities."""
from questfoundry.providers.config import ProviderConfig
from questfoundry.providers.registry import ProviderRegistry
from .workspace import find_workspace

def get_provider_registry() -> ProviderRegistry:
    """Get provider registry from workspace config."""
    workspace = find_workspace()
    config_path = workspace / ".questfoundry" / "config.yml"

    if not config_path.exists():
        raise FileNotFoundError(
            "No provider configuration found. Run 'qf config set' first."
        )

    config = ProviderConfig.from_file(config_path)
    return ProviderRegistry(config)
```

#### 2.2: Loop Command

**File:** `src/qf/commands/loop.py` (~150 lines)

```python
"""Loop execution commands."""
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from questfoundry.orchestrator import Orchestrator
from questfoundry.loops import LoopRegistry

from ..utils.workspace import get_workspace_manager
from ..utils.providers import get_provider_registry

console = Console()
app = typer.Typer(help="Execute loops")

@app.command("run")
def run(
    loop_id: str = typer.Argument(..., help="Loop to execute"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
) -> None:
    """Execute a specific loop."""

    # Get workspace and providers
    ws = get_workspace_manager()
    provider_registry = get_provider_registry()

    # Get default provider
    # TODO: Read from config
    default_provider = "openai"

    # Create orchestrator
    orchestrator = Orchestrator(
        workspace=ws,
        provider_registry=provider_registry
    )
    orchestrator.initialize(provider_name=default_provider)

    # Validate loop exists
    loop_registry = LoopRegistry()
    loops = loop_registry.list_loops()
    loop_meta = next((l for l in loops if l.loop_id == loop_id), None)

    if not loop_meta:
        console.print(f"[red]Unknown loop: {loop_id}[/red]")
        console.print("\n[cyan]Available loops:[/cyan]")
        for meta in loops:
            console.print(f"  {meta.loop_id} - {meta.display_name}")
        raise typer.Exit(1)

    # Display loop info
    console.print(
        Panel(
            f"[bold cyan]{loop_meta.display_name}[/bold cyan]\n"
            f"[dim]{loop_meta.description}[/dim]\n\n"
            f"[yellow]Duration:[/yellow] {loop_meta.typical_duration}\n"
            f"[yellow]Primary roles:[/yellow] {', '.join(loop_meta.primary_roles)}",
            title="Loop Execution",
            border_style="cyan",
        )
    )

    # Execute loop
    console.print(f"\n[cyan]Executing {loop_id}...[/cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running loop...", total=None)

        try:
            # REAL EXECUTION - NOT SIMULATION
            result = orchestrator.execute_loop(loop_id)

            progress.update(task, description="[green]✓ Complete[/green]")

        except Exception as e:
            progress.update(task, description="[red]✗ Failed[/red]")
            console.print(f"\n[red]Error: {e}[/red]")
            raise typer.Exit(1)

    # Display results
    console.print(f"\n[green]✓ Loop complete![/green]")
    console.print(f"Duration: {result.duration}")
    console.print(f"TU created: {result.tu_id}")

    if result.artifacts:
        console.print(f"\n[cyan]Artifacts created:[/cyan]")
        for artifact in result.artifacts:
            console.print(f"  [green]✓[/green] {artifact.id} ({artifact.type})")

    console.print(f"\n[cyan]Next steps:[/cyan]")
    console.print(f"  qf list {result.artifacts[0].type}s")
    console.print(f"  qf show {result.artifacts[0].id}")
    console.print(f"  qf check")

@app.command("list")
def list_loops() -> None:
    """List all available loops."""
    registry = LoopRegistry()
    loops = registry.list_loops()

    console.print(f"\n[cyan]Available loops ({len(loops)}):[/cyan]\n")

    for loop_meta in loops:
        console.print(f"[bold]{loop_meta.loop_id}[/bold] - {loop_meta.display_name}")
        console.print(f"  [dim]{loop_meta.description}[/dim]")
        console.print()

@app.command("info")
def info(
    loop_id: str = typer.Argument(..., help="Loop ID"),
) -> None:
    """Show detailed loop information."""
    registry = LoopRegistry()
    loops = registry.list_loops()
    loop_meta = next((l for l in loops if l.loop_id == loop_id), None)

    if not loop_meta:
        console.print(f"[red]Unknown loop: {loop_id}[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold]{loop_meta.display_name}[/bold]\n\n"
            f"{loop_meta.description}\n\n"
            f"[yellow]Duration:[/yellow] {loop_meta.typical_duration}\n"
            f"[yellow]Primary roles:[/yellow] {', '.join(loop_meta.primary_roles)}\n"
            f"[yellow]Consulted roles:[/yellow] {', '.join(loop_meta.consulted_roles)}\n\n"
            f"[cyan]Entry conditions:[/cyan]\n" +
            "\n".join(f"  • {c}" for c in loop_meta.entry_conditions) + "\n\n"
            f"[cyan]Exit conditions:[/cyan]\n" +
            "\n".join(f"  • {c}" for c in loop_meta.exit_conditions) + "\n\n"
            f"[cyan]Output artifacts:[/cyan]\n" +
            "\n".join(f"  • {a}" for a in loop_meta.output_artifacts),
            title=f"Loop: {loop_id}",
            border_style="cyan",
        )
    )

@app.command("auto")
def auto(
    goal: str = typer.Argument(..., help="Your goal"),
) -> None:
    """Let Orchestrator select appropriate loop for your goal."""

    ws = get_workspace_manager()
    provider_registry = get_provider_registry()

    orchestrator = Orchestrator(
        workspace=ws,
        provider_registry=provider_registry
    )
    orchestrator.initialize(provider_name="openai")

    # Showrunner selects loop
    console.print(f"\n[cyan]Analyzing goal:[/cyan] {goal}\n")

    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
        task = progress.add_task("Consulting Showrunner...", total=None)
        loop_id = orchestrator.select_loop(goal)
        progress.update(task, description=f"[green]Selected: {loop_id}[/green]")

    console.print(f"\n[green]→ Executing {loop_id}[/green]\n")

    # Execute selected loop
    result = orchestrator.execute_loop(loop_id)

    console.print(f"\n[green]✓ Goal accomplished via {loop_id}[/green]")
```

### Deliverable

- [ ] `qf loop run <loop-id>` executes real AI loop
- [ ] `qf loop list` shows all available loops
- [ ] `qf loop info <loop-id>` shows loop details
- [ ] `qf loop auto "<goal>"` - Orchestrator selects loop
- [ ] Real artifacts created in workspace
- [ ] ~200 lines total
- [ ] **NO simulation code**

---

## Phase 3: Artifact Operations (Day 4)

Build commands for browsing and managing artifacts.

**Files:**
- `src/qf/commands/artifact.py` - list, show, search, promote, demote
- `src/qf/formatting/artifacts.py` - Rich display formatters

**~200 lines total**

---

## Phase 4: Quality & Export (Day 5)

Build validation and export commands.

**Files:**
- `src/qf/commands/check.py` - Run Gatekeeper
- `src/qf/commands/export.py` - Export views
- `src/qf/commands/bind.py` - Bind books

**~200 lines total**

---

## Phase 5: Polish (Days 6-7)

- Provider commands (`qf provider list/test/set-default`)
- Debug commands (`qf debug loops/roles/providers`)
- TU commands (`qf tu list/show`)
- Rich formatting improvements
- Shell completion
- Documentation
- Tests

---

## Total Scope

**~800-1000 lines of actual CLI code** (vs 4000+ lines of simulation in old CLI)

The library does all the work. We just display it nicely.

---

## Testing Strategy

### Unit Tests

```python
def test_init_creates_workspace(tmp_path):
    """Test qf init creates real workspace."""
    os.chdir(tmp_path)
    result = runner.invoke(app, ["init", "--name", "Test", "--author", "Alice"])

    assert result.exit_code == 0
    assert (tmp_path / ".questfoundry").exists()
    assert (tmp_path / "test.qfproj").exists()

    # Verify with library
    ws = WorkspaceManager(tmp_path)
    info = ws.get_project_info()
    assert info.name == "Test"
    assert info.author == "Alice"
```

### Integration Tests

```python
@mock_llm_provider
def test_full_loop_execution(tmp_workspace):
    """Test full loop execution creates artifacts."""
    # Setup
    os.chdir(tmp_workspace)
    runner.invoke(app, ["init", "--name", "Test"])
    runner.invoke(app, ["config", "set", "providers.text.default", "mock"])

    # Execute loop
    result = runner.invoke(app, ["loop", "run", "hook-harvest"])
    assert result.exit_code == 0

    # Verify artifacts created
    ws = WorkspaceManager(tmp_workspace)
    artifacts = ws.list_hot_artifacts()
    assert len(artifacts) > 0
    assert any(a.type == "hook_card" for a in artifacts)
```

---

## Migration from Old CLI

### For Users

**Breaking changes:**
- Commands restructured (e.g., `qf run loop-name` → `qf loop run loop-name`)
- Config file format may differ
- Checkpoint system removed (replaced by real TU tracking)

**Migration guide:**
1. Archive old project
2. Initialize new project with `qf init`
3. Copy artifacts manually if needed
4. Reconfigure providers

### For Developers

- Old `src/qf/commands/` archived as `commands_old/`
- New implementation in `src/qf/commands/`
- Can reference formatting utilities from old CLI
- Tests need complete rewrite

---

## Success Metrics

1. **Correctness:** All commands use real library, no simulation
2. **Completeness:** Can init project, run loops, view results, validate, export
3. **Code size:** <1000 lines of CLI code (thin wrapper)
4. **Tests:** >80% coverage with real library integration
5. **Documentation:** Complete README with real examples

---

## The Core Pattern

Every command follows this pattern:

```python
def command(...):
    # 1. Get workspace
    ws = get_workspace_manager()

    # 2. Call library
    result = library_function(...)

    # 3. Display results
    console.print(format_result(result))
```

That's it. No business logic in CLI. Just call → display.

If the library doesn't support something, we either:
1. Contribute to questfoundry-py
2. Mark as future feature
3. Don't implement it

**We never fake it.**
