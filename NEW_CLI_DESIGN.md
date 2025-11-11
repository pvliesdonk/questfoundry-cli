# QuestFoundry CLI - New Design (Reality-Based)

**Date:** 2025-11-11
**Based on:** Actual spec (layers 0-5) + questfoundry-py v0.5.0 implementation

---

## What QuestFoundry Actually Is

**QuestFoundry is an AI-powered authoring system for creating nonlinear, replayable gamebooks** (interactive fiction with branching narratives, hubs, loops, gateways, and codewords).

### Core Concepts

1. **15 AI Roles** work together like a creative studio:
   - **Showrunner** (SR) - Orchestrates all work, triggers loops
   - **Gatekeeper** (GK) - Quality assurance, validates before export
   - **Plotwright** (PW) - Designs story topology (hubs/loops/gateways)
   - **Scene Smith** (SS) - Writes prose in sections
   - **Lore Weaver** (LW) - Manages world canon, resolves contradictions
   - **Codex Curator** (CC) - Creates player-safe encyclopedia entries
   - **Style Lead** (SL) - Maintains voice, tone, visual guardrails
   - **Art Director** (AD) + **Illustrator** (IL) - Plans and creates images
   - **Audio Director** (AuD) + **Audio Producer** (AP) - Plans and creates audio
   - **Researcher** (RS) - Fact-checks, cites sources
   - **Translator** (TR) - Localization
   - **Book Binder** (BB) - Assembles exports
   - **Player-Narrator** (PN) - Delivers spoiler-free player experience

2. **Hot/Cold Workflow**:
   - **Hot SoT** - Work-in-progress (file-based, editable)
   - **Cold SoT** - Stable, validated canon (SQLite, export-ready)
   - Content flows: `Hot → Validation → Cold → Export`

3. **Hooks** - New facts/ideas that flow through a lifecycle:
   - Created by roles (Plotwright, Scene Smith, Lore Weaver)
   - Collected in **Hook Harvest** loop
   - Canonized in **Lore Deepening** loop
   - Published as codex entries in **Codex Expansion** loop

4. **Loops** - Multi-step AI workflows:
   - **Story Spark** - Add/reshape plot
   - **Hook Harvest** - Collect and prioritize ideas
   - **Lore Deepening** - Convert hooks to canon
   - **Codex Expansion** - Create player-safe entries
   - **Style Tune-up** - Fix voice/tone drift
   - **Art Touch-up** - Plan/create illustrations
   - **Audio Pass** - Plan/create audio
   - **Translation Pass** - Localize content
   - **Binding Run** - Export for players
   - **Narration Dry-Run** - Test player experience
   - **Gatecheck** - Run quality validation
   - **Post-Mortem** - Analyze outcomes
   - **Archive Snapshot** - Create archival copy

5. **Quality Bars** - 8 validation checks:
   - Integrity, Reachability, Nonlinearity, Gateways, Style, Determinism, Presentation, Spoiler Hygiene

6. **17 Artifact Types**:
   - hook_card, tu_brief, canon_pack, codex_entry, style_addendum, research_memo
   - shotlist, cuelist, art_plan, audio_plan
   - gatecheck_report, view_log, language_pack, register_map, edit_notes, front_matter, pn_playtest_notes

---

## What questfoundry-py Actually Provides

From studying the v0.5.0 implementation:

### ✅ Fully Available

1. **Orchestrator** - Coordinates loop execution
   ```python
   orchestrator = Orchestrator(workspace, provider_registry)
   orchestrator.initialize(provider)
   loop_id = orchestrator.select_loop(goal="Create a mystery story")
   result = orchestrator.execute_loop(loop_id)
   ```

2. **WorkspaceManager** - Hot/cold storage management
   ```python
   ws = WorkspaceManager("./my-adventure")
   ws.init_workspace(name="Dragon Quest", author="Alice")
   ws.save_hot_artifact(artifact)
   ws.promote_to_cold("HOOK-001")
   ```

3. **LoopRegistry** - Access to all loops
   ```python
   registry = LoopRegistry()
   loops = registry.list_loops()  # Returns 17 loops
   ```

4. **RoleRegistry** - Access to all roles
   ```python
   registry = RoleRegistry(provider_registry)
   lore_weaver = registry.get_role("lore_weaver")
   ```

5. **ProviderRegistry** - LLM/image provider management
   ```python
   config = ProviderConfig.from_file(".questfoundry/config.yml")
   registry = ProviderRegistry(config)
   ```

6. **Gatekeeper** - Quality validation
   ```python
   gatekeeper = Gatekeeper()
   report = gatekeeper.run_gatecheck(artifacts)
   ```

7. **Export System** - ViewGenerator, BookBinder, GitExporter
   ```python
   view_gen = ViewGenerator(ws.cold_store)
   binder = BookBinder()
   ```

---

## The CLI's Job

**The CLI is a thin wrapper that:**

1. **Manages projects** - init, status, config
2. **Triggers loops** - via Orchestrator
3. **Shows progress** - real-time from loop execution
4. **Displays results** - artifacts, quality reports, exports
5. **Configures providers** - OpenAI, Ollama, etc.

**The CLI is NOT:**
- An AI implementation (that's questfoundry-py)
- A simulation (all work is real)
- A duplicate data store (uses WorkspaceManager)

---

## CLI Commands (Reality-Based)

### Project Management

```bash
# Initialize new project
qf init [path] --name "Dragon Quest" --author "Alice"
→ Creates .questfoundry/ workspace
→ Initializes project.qfproj (SQLite)
→ Sets up default config.yml

# Show project status
qf status
→ Shows hot/cold artifact counts
→ Shows recent TUs (time units)
→ Shows active loops
→ Shows quality bar status

# Configuration
qf config set providers.text.default openai
qf config set providers.text.openai.model gpt-4o
qf config list
qf config get providers.text.default

# Provider management
qf provider list
qf provider test openai
qf provider set-default text openai
```

### Loop Execution

```bash
# Execute a specific loop
qf loop run story-spark
qf loop run hook-harvest
qf loop run lore-deepening

# Let Orchestrator choose loop based on goal
qf loop auto "I want to add a dragon to my story"
→ Orchestrator selects appropriate loop
→ Executes with real AI
→ Shows progress

# Interactive mode (agent can ask questions)
qf loop run hook-harvest --interactive

# List available loops
qf loop list
qf loop info story-spark
```

### Artifact Management

```bash
# List artifacts
qf list hooks
qf list canon
qf list codex
qf list tus
qf list all

# Show artifact details
qf show HOOK-001
qf show TU-2025-11-07-SR01
qf show CANON-042

# Search artifacts
qf search "dragon"
qf search --type hook_card --status proposed

# Promote to cold (after validation)
qf promote HOOK-001

# Demote back to hot (for editing)
qf demote HOOK-001
```

### Quality & Validation

```bash
# Run gatecheck
qf check
qf check --bars integrity,reachability,style

# Validate specific artifact
qf validate HOOK-001

# Show quality reports
qf report gatecheck
```

### Export & Views

```bash
# Generate view
qf export view --snapshot latest --format html
qf export view --snapshot SNAP-001 --format markdown --output story.md

# Export to Git
qf export git --output ./git-export/

# Bind book (assemble for players)
qf bind --snapshot latest --format epub --output dragon-quest.epub
```

### Development & Debug

```bash
# Show detailed info
qf info  # Project metadata
qf workspace  # Workspace structure
qf tu list  # Time units

# Developer tools
qf debug loops  # Show loop metadata
qf debug roles  # Show role info
qf debug providers  # Show provider status
```

---

## Implementation Approach

### Phase 1: Foundation (Day 1)

**Goal:** Minimal working prototype

```
qf init      → WorkspaceManager.init_workspace()
qf status    → WorkspaceManager queries
qf config    → YAML file operations
```

**No AI calls yet. Just project management.**

### Phase 2: Loop Execution (Days 2-3)

**Goal:** Real loop execution with Orchestrator

```python
# src/qf/commands/loop.py

from questfoundry.orchestrator import Orchestrator
from questfoundry.state import WorkspaceManager
from questfoundry.providers.config import ProviderConfig
from questfoundry.providers.registry import ProviderRegistry

def run(loop_id: str, interactive: bool = False):
    # Load workspace
    ws = WorkspaceManager(find_workspace())

    # Load providers
    config = ProviderConfig.from_file(ws.path / ".questfoundry" / "config.yml")
    providers = ProviderRegistry(config)

    # Create orchestrator
    orchestrator = Orchestrator(ws, providers)
    orchestrator.initialize(provider_name="openai")  # From config

    # Execute loop
    with Progress() as progress:
        task = progress.add_task(f"Running {loop_id}...", total=None)

        result = orchestrator.execute_loop(loop_id)

        progress.update(task, description="[green]✓ Complete[/green]")

    # Display results
    console.print(f"\n[green]✓ {loop_id} complete[/green]")
    console.print(f"Duration: {result.duration}")
    console.print(f"Artifacts created: {len(result.artifacts)}")
    for artifact in result.artifacts:
        console.print(f"  - {artifact.id}: {artifact.type}")
```

**This is ~40 lines. Not 178. Real integration.**

### Phase 3: Artifact Operations (Day 4)

```python
# src/qf/commands/artifact.py

def list_artifacts(artifact_type: str = "all"):
    ws = WorkspaceManager(find_workspace())

    if artifact_type == "hooks":
        artifacts = ws.list_hot_artifacts(type="hook_card")
    elif artifact_type == "all":
        artifacts = ws.list_hot_artifacts()

    # Display in table
    table = Table()
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Status")

    for art in artifacts:
        table.add_row(art.id, art.type, art.metadata.get("status", "unknown"))

    console.print(table)
```

### Phase 4: Quality & Export (Day 5)

```python
# src/qf/commands/check.py

from questfoundry.validation import Gatekeeper

def check(bars: list[str] | None = None):
    ws = WorkspaceManager(find_workspace())
    artifacts = ws.list_hot_artifacts()

    gatekeeper = Gatekeeper()
    report = gatekeeper.run_gatecheck(artifacts, bars=bars)

    # Display report
    for bar, result in report.results.items():
        status = "[green]✓[/green]" if result.passed else "[red]✗[/red]"
        console.print(f"{status} {bar}: {result.message}")
```

### Phase 5: Polish (Days 6-7)

- Rich formatting
- Progress tracking
- Interactive prompts
- Shell completion
- Documentation

---

## Command Structure

```
qf/
  cli.py                 # Main Typer app

  commands/
    init.py             # qf init
    status.py           # qf status
    config.py           # qf config
    provider.py         # qf provider

    loop.py             # qf loop run/auto/list/info
    artifact.py         # qf list/show/search/promote/demote
    check.py            # qf check/validate/report
    export.py           # qf export
    bind.py             # qf bind

    debug.py            # qf debug/info/workspace/tu

  formatting/
    tables.py           # Rich tables
    panels.py           # Rich panels
    progress.py         # Progress bars

  utils/
    workspace.py        # Find workspace helper
    config.py           # Config file helpers
    display.py          # Display formatters
```

---

## Key Differences from Old CLI

### OLD (Wrong)

```python
# Simulation!
time.sleep(0.2)
progress_tracker.start_step("Context initialization", "Lore Weaver")
time.sleep(0.3)
# ... fake progress
```

```yaml
# Duplicate data!
loops.yml:
  story-spark:
    display_name: Story Spark
    description: Generate story concepts
    # ... duplicating library data
```

### NEW (Right)

```python
# Real execution!
orchestrator = Orchestrator(workspace, providers)
result = orchestrator.execute_loop("story-spark")
# Real AI runs, real artifacts created
```

```python
# Use library data!
registry = LoopRegistry()
loops = registry.list_loops()
for loop in loops:
    console.print(f"{loop.loop_id}: {loop.description}")
```

---

## Success Criteria

### Must Have

- [ ] `qf init` creates real workspace with WorkspaceManager
- [ ] `qf loop run <loop>` executes real AI loop via Orchestrator
- [ ] `qf list` queries real workspace artifacts
- [ ] `qf show <id>` displays real artifact data
- [ ] `qf check` runs real Gatekeeper validation
- [ ] `qf export` creates real views/exports
- [ ] NO simulation code anywhere
- [ ] NO duplicate data (loops.yml, etc.)
- [ ] NO "coming soon" messages
- [ ] Real progress from actual loop execution

### Should Have

- [ ] `qf loop auto <goal>` - Orchestrator selects loop
- [ ] `qf config` - Manage provider configuration
- [ ] Rich formatting for all outputs
- [ ] Shell completion
- [ ] Good error messages

### Nice to Have

- [ ] `qf loop run --interactive` - Agent asks questions
- [ ] `qf promote/demote` - Hot/cold management
- [ ] `qf search` - Query artifacts
- [ ] TUI mode (future)

---

## Timeline

**7 days total:**

- **Day 1:** Phase 1 - Foundation (init, status, config)
- **Days 2-3:** Phase 2 - Loop execution (THE critical feature)
- **Day 4:** Phase 3 - Artifact operations
- **Day 5:** Phase 4 - Quality & export
- **Days 6-7:** Phase 5 - Polish, docs, tests

---

## Core Principles

1. **Reality-based** - Use actual questfoundry-py, not spec examples
2. **Thin wrapper** - CLI adds UX, not logic
3. **No simulation** - Everything is real or it doesn't exist
4. **No duplication** - Use library registries, don't copy data
5. **Show, don't fake** - Display real results, not mock progress

---

## Next Steps

1. Archive old `src/qf/commands/` as `src/qf/commands_old/`
2. Create new minimal `commands/` directory
3. Implement Phase 1 (foundation)
4. Build Phase 2 (loop execution) - THE KEY INTEGRATION
5. Expand incrementally

Once Phase 2 works (real loop execution), the rest is just formatting.

---

## Questions Answered

**Q: How do loops actually execute?**
A: Via `Orchestrator.execute_loop(loop_id)` - it's all there in questfoundry-py

**Q: Where are loop definitions?**
A: In `LoopRegistry.list_loops()` - returns 17 LoopMetadata objects

**Q: How to initialize workspace?**
A: `WorkspaceManager.init_workspace(name, author)` - creates .questfoundry/ and project.qfproj

**Q: How to run quality checks?**
A: `Gatekeeper().run_gatecheck(artifacts)` - returns GatecheckReport

**Q: How to create exports?**
A: `ViewGenerator(cold_store).generate_view(snapshot_id)` + `BookBinder().render_html(view)`

**All answered by reading the actual library code.**

---

## The Bottom Line

**Previous CLI:** Built on outdated specs, simulated everything
**New CLI:** Built on actual library, wraps real functionality

**Complexity reduction:**
- `run.py`: 178 lines → ~40 lines (no simulation)
- `loops.yml`: 83 lines → DELETE (use LoopRegistry)
- `quickstart.py`: Simulation → Real loop chaining

**The library does the work. The CLI just shows it to users.**

That's what "thin wrapper" actually means.
