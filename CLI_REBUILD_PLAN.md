# QuestFoundry CLI Rebuild Plan

**Status:** Ready to Execute
**Estimated Time:** 5-7 days
**Approach:** Study library first, then build incrementally

---

## Phase 0: Library Investigation (Day 1)

Before writing any CLI code, we must understand how questfoundry-py v0.5.0 **actually** works.

### Tasks

#### 0.1: Read Source Code (2-3 hours)

**Clone and explore questfoundry-py:**

```bash
cd /tmp
git clone https://github.com/pvliesdonk/questfoundry-py
cd questfoundry-py
git checkout v0.5.0  # Or whatever commit is installed
```

**Files to read:**

1. `src/questfoundry/loops/base.py`
   - How is `Loop` class defined?
   - What does `Loop.execute()` require?
   - What does `LoopContext` contain?
   - What does `LoopResult` return?

2. `src/questfoundry/loops/registry.py`
   - How are loops registered?
   - Is there a `.get_loop(id)` method?
   - How to instantiate a Loop from registry?

3. `src/questfoundry/state/workspace.py`
   - How does `WorkspaceManager.init_workspace()` work?
   - What's the workspace directory structure?
   - How to save/load artifacts?

4. `src/questfoundry/roles/base.py`
   - How does `Role.execute()` work?
   - What's in `RoleContext`?
   - What's in `RoleResult`?

5. `src/questfoundry/providers/registry.py`
   - How to configure providers?
   - How to query available providers?

**Document findings in:** `docs/QUESTFOUNDRY_PY_API.md`

---

#### 0.2: Write Exploration Scripts (2 hours)

**Script 1: Loop Execution**

```python
# scripts/explore_loops.py
"""
Figure out how to execute a loop in questfoundry-py v0.5.0
"""
from questfoundry.loops import LoopRegistry, Loop, LoopContext
from questfoundry.state import WorkspaceManager
from pathlib import Path

# Create a test workspace
workspace_path = Path("/tmp/test-quest")
workspace_path.mkdir(exist_ok=True)

# Initialize workspace
ws = WorkspaceManager.init_workspace(workspace_path)

# Get loop registry
registry = LoopRegistry()
loops = registry.list_loops()

print("Available loops:")
for loop_meta in loops:
    print(f"  - {loop_meta.loop_id}: {loop_meta.display_name}")

# Try to execute a simple loop
# TODO: Figure out the exact pattern
try:
    # Hypothesis 1: Loop is instantiated separately
    # loop = Loop(...)

    # Hypothesis 2: Registry provides a factory
    # loop = registry.create_loop("hook_harvest")

    # Hypothesis 3: Loop is executed through workspace
    # result = ws.execute_loop("hook_harvest", context)

    print("\nAttempting to execute hook_harvest...")
    # ... actual code here

except Exception as e:
    print(f"Error: {e}")
    print("Need to investigate further")
```

**Run and iterate until loop execution works.**

---

**Script 2: Workspace Operations**

```python
# scripts/explore_workspace.py
"""
Test WorkspaceManager operations
"""
from questfoundry.state import WorkspaceManager, ProjectInfo
from pathlib import Path

workspace_path = Path("/tmp/test-quest")
workspace_path.mkdir(exist_ok=True)

# Initialize
ws = WorkspaceManager.init_workspace(workspace_path)

# Set project info
project_info = ProjectInfo(
    name="Test Quest",
    description="A test quest for exploration",
    version="0.1.0"
)
ws.save_project_info(project_info)

# List artifacts
print("Hot artifacts:", ws.list_hot_artifacts())
print("Cold artifacts:", ws.list_cold_artifacts())
print("TUs:", ws.list_tus())

# Try saving an artifact
# ... test artifact operations
```

---

**Script 3: Role Execution**

```python
# scripts/explore_roles.py
"""
Test role execution (we know this works from generate.py)
"""
from questfoundry.roles import RoleRegistry, RoleContext, RoleResult
from questfoundry.providers import ProviderRegistry, ProviderConfig
from questfoundry.models import Artifact

# Setup (based on working generate.py code)
provider_config = ProviderConfig(...)  # TODO: Configure
provider_registry = ProviderRegistry(provider_config)
role_registry = RoleRegistry(provider_registry)

# Create context
context = RoleContext(
    artifacts={"input": Artifact(...)},
    parameters={}
)

# Execute role
lore_weaver = role_registry.get_role("lore_weaver")
result = lore_weaver.execute(context)

print("Success:", result.success)
print("Output:", result.output)
```

---

#### 0.3: Document Findings (1 hour)

**Create:** `docs/QUESTFOUNDRY_PY_API.md`

```markdown
# questfoundry-py v0.5.0 API Documentation

## Loop Execution

### Pattern

[Document the actual working pattern]

### Example

[Paste working code from exploration script]

## Workspace Management

### Initialization

[Document WorkspaceManager.init_workspace()]

### Artifact Operations

[Document save/load methods]

## Provider Configuration

[Document how to set up providers]

## Role Execution

[Document RoleRegistry and Role.execute()]
```

---

**Deliverable:** Complete understanding of library API, with working code examples

---

## Phase 1: Minimal Working Prototype (Day 2)

Build the absolute minimum to prove the concept works.

### Goal

A CLI with just 2 commands that **actually work**:
- `qf init` - Creates a real workspace
- `qf run hook-harvest` - Executes a real loop

**No simulation. No fake progress bars. Real integration only.**

---

### Tasks

#### 1.1: Project Setup

**Keep from old CLI:**
- `pyproject.toml` (already has correct dependencies)
- `tests/` infrastructure
- Basic Typer app structure

**Clean up:**
```bash
# Rename old commands directory
mv src/qf/commands src/qf/commands_old

# Create new commands directory
mkdir src/qf/commands
touch src/qf/commands/__init__.py
```

---

#### 1.2: Implement `qf init`

**File:** `src/qf/commands/init.py` (~50 lines)

```python
"""Project initialization command."""
from pathlib import Path
import typer
from rich.console import Console
from questfoundry.state import WorkspaceManager, ProjectInfo

console = Console()

def init(
    path: Path = typer.Argument(Path.cwd(), help="Project directory"),
    name: str = typer.Option(None, help="Project name"),
) -> None:
    """Initialize a new QuestFoundry project."""

    # Check if project already exists
    qfproj = path / f"{path.name}.qfproj"
    if qfproj.exists():
        console.print(f"[red]Error: Project already exists at {qfproj}[/red]")
        raise typer.Exit(1)

    # Prompt for name if not provided
    if not name:
        name = typer.prompt("Project name", default=path.name)

    description = typer.prompt("Project description", default="")

    # Initialize workspace using library
    ws = WorkspaceManager.init_workspace(path)

    # Save project info
    project_info = ProjectInfo(
        name=name,
        description=description,
        version="0.1.0"
    )
    ws.save_project_info(project_info)

    console.print(f"\n[green]✓ Project initialized: {qfproj}[/green]")
    console.print(f"\n[cyan]Next steps:[/cyan]")
    console.print(f"  cd {path}")
    console.print(f"  qf run hook-harvest")
```

**Test:**
```bash
$ qf init /tmp/test-quest
Project name: Test Quest
Project description: A test quest

✓ Project initialized: /tmp/test-quest/test-quest.qfproj

Next steps:
  cd /tmp/test-quest
  qf run hook-harvest
```

**Acceptance criteria:**
- [ ] Creates real `.qfproj` file
- [ ] Creates `.questfoundry/` directory
- [ ] Uses WorkspaceManager (no manual file creation)
- [ ] No simulation

---

#### 1.3: Implement `qf run`

**File:** `src/qf/commands/run.py` (~80 lines total, not 178!)

```python
"""Loop execution command."""
from pathlib import Path
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from questfoundry.loops import LoopRegistry
from questfoundry.state import WorkspaceManager

from ..utils import find_project_file

console = Console()

def run(
    loop_name: str = typer.Argument(..., help="Loop to execute"),
) -> None:
    """Execute a loop."""

    # Find project
    project_file = find_project_file()
    if not project_file:
        console.print("[red]No project found. Run 'qf init' first.[/red]")
        raise typer.Exit(1)

    # Get loop from registry
    registry = LoopRegistry()
    loops = registry.list_loops()

    # Find matching loop
    loop_meta = None
    for meta in loops:
        if meta.loop_id == loop_name or meta.display_name.lower() == loop_name.lower():
            loop_meta = meta
            break

    if not loop_meta:
        console.print(f"[red]Unknown loop: {loop_name}[/red]")
        console.print("\n[cyan]Available loops:[/cyan]")
        for meta in loops:
            console.print(f"  {meta.loop_id} - {meta.display_name}")
        raise typer.Exit(1)

    # Execute loop (using pattern discovered in Phase 0)
    console.print(f"\n[cyan]Executing: {loop_meta.display_name}[/cyan]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running loop...", total=None)

        try:
            # TODO: Replace with actual pattern from Phase 0
            # Example (will vary based on actual API):
            ws = WorkspaceManager(project_file.parent)
            context = LoopContext(workspace=ws, ...)
            loop = ...  # Get or create loop instance
            result = loop.execute(context)

            progress.update(task, description="[green]✓ Complete[/green]")

            # Display results
            console.print(f"\n[green]Loop complete![/green]")
            console.print(f"Duration: {result.duration}")
            console.print(f"Artifacts created: {len(result.artifacts)}")

        except Exception as e:
            progress.update(task, description="[red]✗ Failed[/red]")
            console.print(f"\n[red]Error: {e}[/red]")
            raise typer.Exit(1)
```

**Key points:**
- ✅ Uses real LoopRegistry
- ✅ Uses real loop execution (pattern from Phase 0)
- ✅ Real progress from loop events (not time.sleep)
- ✅ ~80 lines total (vs 178 in old version)
- ❌ No simulation whatsoever

**Test:**
```bash
$ cd /tmp/test-quest
$ qf run hook-harvest

Executing: Hook Harvest
⠋ Running loop...
[Real loop execution happens]
✓ Complete

Loop complete!
Duration: 00:02:34
Artifacts created: 5
```

**Acceptance criteria:**
- [ ] Executes real loop from library
- [ ] Creates real artifacts in workspace
- [ ] No time.sleep() calls
- [ ] Shows real results

---

#### 1.4: Test End-to-End

```bash
# Full workflow
$ qf init /tmp/my-quest
$ cd /tmp/my-quest
$ qf run hook-harvest
$ ls .questfoundry/hot/hooks/
HOOK-001.json  HOOK-002.json  ...

# Verify artifacts are REAL
$ cat .questfoundry/hot/hooks/HOOK-001.json
{
  "id": "HOOK-001",
  "type": "hook_card",
  ... real generated content ...
}
```

**Acceptance criteria:**
- [ ] Full workflow works
- [ ] Real artifacts created
- [ ] AI actually ran (not simulated)
- [ ] Can verify in workspace files

---

**Deliverable:** Working prototype with real integration

---

## Phase 2: Core Commands (Days 3-4)

Build remaining essential commands with real integration.

### Tasks

#### 2.1: `qf status` (Day 3 morning)

**File:** `src/qf/commands/status.py` (~60 lines)

```python
"""Project status command."""
from questfoundry.state import WorkspaceManager
from rich.console import Console
from rich.table import Table

def status() -> None:
    """Show project status."""

    ws = WorkspaceManager(find_workspace())

    # Get project info
    info = ws.get_project_info()
    console.print(f"\n[cyan]Project:[/cyan] {info.name}")
    console.print(f"[cyan]Description:[/cyan] {info.description}")

    # List artifacts (using workspace manager)
    hot_artifacts = ws.list_hot_artifacts()
    console.print(f"\n[cyan]Hot artifacts:[/cyan] {len(hot_artifacts)}")

    # List TUs
    tus = ws.list_tus()
    console.print(f"[cyan]Time units:[/cyan] {len(tus)}")

    # Show recent activity
    if tus:
        console.print("\n[cyan]Recent activity:[/cyan]")
        for tu in tus[-5:]:  # Last 5 TUs
            console.print(f"  {tu.id} - {tu.role} - {tu.timestamp}")
```

---

#### 2.2: `qf list` (Day 3 morning)

**File:** `src/qf/commands/list.py` (~80 lines)

```python
"""Artifact listing command."""
from questfoundry.state import WorkspaceManager
from rich.table import Table

def list_artifacts(
    artifact_type: str = typer.Argument("all", help="Type: hooks, canon, tus, all"),
) -> None:
    """List artifacts in workspace."""

    ws = WorkspaceManager(find_workspace())

    if artifact_type in ("hooks", "all"):
        hooks = ws.list_hot_artifacts(type="hook_card")
        display_hooks_table(hooks)

    if artifact_type in ("canon", "all"):
        canon = ws.list_hot_artifacts(type="canon_pack")
        display_canon_table(canon)

    # ... etc
```

---

#### 2.3: `qf show` (Day 3 afternoon)

**File:** `src/qf/commands/show.py` (~100 lines)

```python
"""Artifact inspection command."""
from questfoundry.state import WorkspaceManager
from rich.panel import Panel

def show(
    artifact_id: str = typer.Argument(..., help="Artifact ID"),
) -> None:
    """Show artifact details."""

    ws = WorkspaceManager(find_workspace())

    # Load artifact from workspace
    artifact = ws.get_hot_artifact(artifact_id)
    if not artifact:
        artifact = ws.get_cold_artifact(artifact_id)

    if not artifact:
        console.print(f"[red]Artifact not found: {artifact_id}[/red]")
        raise typer.Exit(1)

    # Display based on type
    if artifact.type == "hook_card":
        display_hook(artifact)
    elif artifact.type == "canon_pack":
        display_canon(artifact)
    # ... etc
```

---

#### 2.4: `qf quickstart` (Day 4)

**File:** `src/qf/commands/quickstart.py` (~150 lines)

**Key changes:**
- Remove `_simulate_loop_execution()` function entirely
- Use real loop execution from Phase 1
- Keep interactive prompts (they're good)
- Remove checkpoint simulation (use real workspace state)

```python
"""Quickstart workflow."""
from questfoundry.loops import LoopRegistry
from questfoundry.state import WorkspaceManager

def quickstart() -> None:
    """Guided quickstart workflow."""

    # Prompts (keep from old code)
    premise = ask_premise()
    tone = ask_tone()
    length = ask_length()
    project_name = ask_project_name(premise)

    # Create project (using Phase 1 code)
    ws = WorkspaceManager.init_workspace(Path.cwd())
    ws.save_project_info(ProjectInfo(name=project_name, ...))

    # Execute loops FOR REAL
    registry = LoopRegistry()

    for loop_name in ["hook_harvest", "lore_deepening", "story_spark"]:
        console.print(f"\n[cyan]Starting {loop_name}...[/cyan]")

        # REAL execution (not simulation!)
        loop = registry.get_loop(loop_name)  # Or whatever pattern from Phase 0
        result = loop.execute(context)

        # Show real results
        console.print(f"[green]✓ {loop_name} complete[/green]")
        console.print(f"  Artifacts: {len(result.artifacts)}")

        # Ask to continue
        if not ask_continue():
            break
```

---

**Deliverable:** Full set of working commands, all with real integration

---

## Phase 3: Polish & Advanced Features (Days 5-6)

### Tasks

#### 3.1: Generate Commands (Day 5 morning)

**Status:** Already works! (`src/qf/commands/generate.py`)

**Tasks:**
- Copy from old CLI (it's correct)
- Remove any "Layer 6 coming soon" messages if present
- Ensure it uses current workspace correctly

---

#### 3.2: Export/Bind Commands (Day 5 afternoon)

**Files:** `src/qf/commands/export.py`, `src/qf/commands/bind.py`

**Replace placeholder code with:**

```python
"""Export command."""
from questfoundry.roles import RoleRegistry

def bind_view(
    snapshot_id: str,
    format: str = "html",
) -> None:
    """Bind a view using BookBinder role."""

    # Use BookBinder role (like generate commands)
    role_registry = get_role_registry()
    book_binder = role_registry.get_role("book_binder")

    context = RoleContext(
        artifacts={"snapshot": load_snapshot(snapshot_id)},
        parameters={"format": format}
    )

    result = book_binder.execute(context)

    # Save output
    output_path = Path(f"view-{snapshot_id}.{format}")
    output_path.write_text(result.output)

    console.print(f"[green]✓ View bound: {output_path}[/green]")
```

---

#### 3.3: Check Command (Day 6 morning)

**File:** `src/qf/commands/check.py`

**Use Gatekeeper role:**

```python
"""Quality check command."""
from questfoundry.roles import RoleRegistry

def check() -> None:
    """Run quality checks."""

    # Use Gatekeeper role
    role_registry = get_role_registry()
    gatekeeper = role_registry.get_role("gatekeeper")

    # Get all artifacts to check
    ws = WorkspaceManager(find_workspace())
    artifacts = ws.list_hot_artifacts()

    context = RoleContext(
        artifacts={"artifacts": artifacts},
        parameters={}
    )

    result = gatekeeper.execute(context)

    # Display quality bar results
    display_quality_report(result.output)
```

---

#### 3.4: Formatting & UX (Day 6 afternoon)

**Port from old CLI:**
- ✅ `src/qf/formatting/` - Keep all formatting utilities
- ✅ `src/qf/interactive/prompts.py` - Keep prompt definitions
- ✅ Progress tracking patterns (adapt to real events)

**Update:**
- Remove simulation-specific formatters
- Adapt to real loop results instead of fake data

---

#### 3.5: Shell Completion (Day 6 afternoon)

**Status:** Already works!

**Port from old CLI:**
- ✅ `src/qf/completions/` - Shell completion system
- Update dynamic completions to use real workspace queries

---

#### 3.6: Documentation (Day 6 evening)

**Update:**
- `README.md` - Updated examples with real commands
- Remove all "Layer 6 coming soon" references
- Add actual usage examples
- Document integration approach

---

**Deliverable:** Polished, feature-complete CLI

---

## Phase 4: Testing & Release (Day 7)

### Tasks

#### 4.1: Update Tests

**Strategy:**
- Keep test infrastructure from old CLI
- Rewrite test expectations for real integration
- Mock LLM providers (not the library itself)

**Example:**

```python
# Old test (testing simulation)
def test_run_loop_shows_progress():
    result = runner.invoke(app, ["run", "hook-harvest"])
    assert "time.sleep" was called  # BAD

# New test (testing real integration)
def test_run_loop_creates_artifacts(tmp_workspace):
    # Setup real workspace
    WorkspaceManager.init_workspace(tmp_workspace)

    # Mock LLM provider
    with mock_provider():
        result = runner.invoke(app, ["run", "hook-harvest"])

    # Verify REAL artifacts created
    artifacts = list(tmp_workspace.glob(".questfoundry/hot/hooks/*.json"))
    assert len(artifacts) > 0
```

---

#### 4.2: Integration Tests

**Create:** `tests/integration/test_full_workflow.py`

```python
def test_full_quickstart_workflow(tmp_path):
    """Test complete workflow from init to export."""

    os.chdir(tmp_path)

    # Init project
    result = runner.invoke(app, ["init"], input="Test\nA test\n")
    assert result.exit_code == 0

    # Run loop
    with mock_provider():
        result = runner.invoke(app, ["run", "hook-harvest"])
        assert result.exit_code == 0

    # Verify artifacts
    hooks = list(tmp_path.glob(".questfoundry/hot/hooks/*.json"))
    assert len(hooks) > 0

    # List artifacts
    result = runner.invoke(app, ["list", "hooks"])
    assert "HOOK-" in result.stdout

    # Show artifact
    hook_id = # ... get from list
    result = runner.invoke(app, ["show", hook_id])
    assert result.exit_code == 0
```

---

#### 4.3: CI/CD

**Ensure:**
- All tests pass with real library (mocked LLMs)
- Type checking passes
- Linting passes
- Coverage > 80%

---

#### 4.4: Documentation

**Create:**
- Updated `README.md`
- `CHANGELOG.md` - Note breaking changes from v0.1
- Migration guide for users of old CLI

---

**Deliverable:** Production-ready CLI

---

## Success Criteria

### Must Have

- [ ] `qf init` creates real workspace using WorkspaceManager
- [ ] `qf run <loop>` executes real loop from library
- [ ] `qf quickstart` runs real loops, creates real artifacts
- [ ] `qf generate` commands work (already do)
- [ ] `qf list/show/status` query real workspace
- [ ] NO `time.sleep()` calls anywhere
- [ ] NO placeholder messages about "Layer 6 coming soon"
- [ ] NO `loops.yml` file (use LoopRegistry)
- [ ] All tests pass with real library integration

### Should Have

- [ ] `qf check` uses Gatekeeper role
- [ ] `qf export/bind` use BookBinder role
- [ ] Shell completion works
- [ ] Good error messages
- [ ] Rich formatting/progress bars

### Nice to Have

- [ ] Interactive mode (if library supports)
- [ ] Provider configuration commands
- [ ] Diff/comparison tools
- [ ] TUI mode (future)

---

## Risk Mitigation

### Risk: Loop execution API is complex

**Mitigation:** Phase 0 investigation ensures we understand it before building

### Risk: Library missing features spec promised

**Mitigation:** Build MVP first, document gaps, contribute upstream if needed

### Risk: Breaking changes from old CLI

**Mitigation:** Document migration path, version as v0.2.0 (breaking)

---

## Rollout Strategy

### Option A: New Branch

- Branch: `rebuild-v0.2`
- Keep old `main` branch
- Merge when ready
- Tag as `v0.2.0`

### Option B: New Repo (Recommended)

- New repo: `questfoundry-cli-v2`
- Clean history
- Old repo archived
- Port good code incrementally

---

## Summary

**Timeline:**
- Day 1: Investigate library (Phase 0)
- Day 2: Minimal prototype (Phase 1)
- Days 3-4: Core commands (Phase 2)
- Days 5-6: Polish (Phase 3)
- Day 7: Testing (Phase 4)

**Total: 5-7 days**

**Approach:**
1. ✅ Study library source code first
2. ✅ Write working exploration scripts
3. ✅ Build minimal prototype with REAL integration
4. ✅ Expand incrementally
5. ✅ Port good UX from old CLI
6. ✅ Test with real library (mock LLMs only)

**Principle:**
**No simulation. No placeholders. Real integration from day 1.**

If a feature can't be implemented with the library, **document the gap** and either:
- Contribute to upstream library
- Mark as "coming soon" with GitHub issue link
- Defer to future version

**Do not fake it.**
