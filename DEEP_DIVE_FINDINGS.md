# QuestFoundry CLI - Deep Dive Analysis Report

**Date:** 2025-11-11
**Branch:** `claude/project-deep-dive-011CV2SD4HcVg8445vQ3uWjg`
**questfoundry-py version:** 0.5.0 (upgraded from 0.4.0)

## Executive Summary

This CLI is **NOT** a thin wrapper around questfoundry-py. It contains extensive simulation code, duplicated data structures, and placeholder implementations that should be delegating to the library. The "Layer 6" references throughout the codebase are based on a fundamental misconception - **Layer 6 (questfoundry-py) has been complete and available all along**.

### Key Findings

1. **Loop execution is completely simulated** - Uses `time.sleep()` instead of the Orchestrator
2. **Loop definitions are duplicated** - CLI maintains its own `loops.yml` instead of using LoopRegistry
3. **Core functionality is stubbed out** - Export, binding, quality checks all have placeholder implementations
4. **Misconception about Layer 6** - Comments say "once Layer 6 arrives" but v0.5.0 has been released with full functionality

## What questfoundry-py v0.5.0 Actually Provides

After installing and testing v0.5.0, here's what's **actually available**:

### ✅ Fully Available Components

1. **Loop System** (`questfoundry.loops`)
   - `LoopRegistry` with 11 pre-defined loops
   - `Loop`, `LoopContext`, `LoopResult`, `LoopMetadata`
   - Complete loop execution framework

2. **Role System** (`questfoundry.roles`)
   - `RoleRegistry` with all roles
   - `RoleContext`, `RoleResult`
   - Text-based roles fully functional (SceneSmith, LoreWeaver, Plotwright, etc.)

3. **State Management** (`questfoundry.state`)
   - `WorkspaceManager` - Complete workspace initialization and management
   - `SQLiteStore`, `FileStore` - Multiple storage backends
   - `EntityRegistry` - Entity tracking
   - `TimelineManager` - Timeline/TU management
   - `ConflictDetector` - Lore consistency checking
   - `ConstraintManifestGenerator` - Constraint tracking

4. **Provider System** (`questfoundry.providers`)
   - `ProviderRegistry` - Provider management
   - `TextProvider`, `ImageProvider` - Base provider abstractions
   - Audio provider support

5. **Validation** (`questfoundry.validators`)
   - Schema validation functions
   - Artifact validation

6. **Models** (`questfoundry.models`)
   - All artifact models (Artifact, HookCard, TUBrief, etc.)

### ❌ NOT Available (Misconception)

- **No `questfoundry.orchestration.Showrunner`** - This module doesn't exist
- Loop orchestration is in `questfoundry.loops`, not a separate orchestration module

## Critical Integration Gaps

### 1. Loop Execution - Completely Simulated

**File:** `src/qf/commands/run.py`

**Current state:**
```python
# Lines 113-117
console.print(
    "\n[yellow]Note: Full loop execution will integrate with questfoundry-py "
    "Showrunner in a future release.[/yellow]"
)

# Lines 119-177 - ALL FAKE
progress_tracker = LoopProgressTracker(loop_name=loop_info['display_name'])
progress_tracker.start_loop()
time.sleep(0.2)  # Simulating work
time.sleep(0.3)  # More fake work
time.sleep(0.2)  # Still fake
```

**What it SHOULD do:**
```python
from questfoundry.loops import LoopRegistry, LoopContext
from questfoundry.state import WorkspaceManager

registry = LoopRegistry()
workspace = WorkspaceManager(workspace_path)

loop = registry.get_loop(loop_id)
context = LoopContext(
    workspace=workspace,
    parameters=user_params
)
result = loop.execute(context)
```

**Impact:** Users think they're running loops, but nothing actually happens. No artifacts are generated, no AI is called, no real work is done.

### 2. Loop Definitions - Duplicated Data

**File:** `src/qf/data/loops.yml` (83 lines)

**Current state:**
- CLI maintains its own YAML file with 13 loops
- Hardcoded display names, abbreviations, categories, descriptions
- Loaded at runtime via `_load_loops()`

**questfoundry-py provides:**
- `LoopRegistry.list_loops()` returns 11 `LoopMetadata` objects
- Each has: `loop_id`, `display_name`, `description`, `typical_duration`, `primary_roles`, `consulted_roles`, `entry_conditions`, `exit_conditions`, `output_artifacts`, `inputs`, `tags`

**Gap:** CLI has 13 loops, library has 11. Need to reconcile:
- CLI has: all 13 from spec
- Library has: `story_spark`, `hook_harvest`, `lore_deepening`, `codex_expansion`, `binding_run`, `style_tune_up`, `art_touch_up`, `audio_pass`, `translation_pass`, `narration_dry_run`, `full_production_run`
- Missing from library: `gatecheck` (GC), `post-mortem` (PM), `archive-snapshot` (AS)?

**Action required:** Delete `loops.yml` and use `LoopRegistry` exclusively, OR contribute missing loops upstream.

### 3. Quickstart - Simulated Workflow

**File:** `src/qf/commands/quickstart.py`

**Lines 95-126:** Entire `_simulate_loop_execution()` function is fake
```python
def _simulate_loop_execution(loop_name: str) -> None:
    """Simulate loop execution with placeholder.

    This will be replaced with actual Layer 6 Showrunner integration.
    """
    time.sleep(1.5)
    progress.update(task, description="[green]✓[/green] Loop complete")
```

**Lines 225-229:** Message about "coming with Layer 6 integration"
```python
console.print(
    "[yellow]Note: Full Showrunner integration (dynamic loop sequencing) "
    "coming with Layer 6 integration.[/yellow]\n"
)
```

**Lines 231-235:** Hardcoded loop sequence
```python
suggested_loops = [
    "Hook Harvest",
    "Lore Deepening",
    "Story Spark",
]
```

**Reality:** questfoundry-py has loop execution available NOW. This message is misleading.

### 4. Project Initialization - Manual Implementation

**File:** `src/qf/interactive/session.py`

**Lines 63-82:** Manually creates workspace structure
```python
# Manually create directories
workspace.mkdir(exist_ok=True)
(workspace / "hot").mkdir(exist_ok=True)
(workspace / "hot" / "hooks").mkdir(exist_ok=True)
# ... etc
```

**Should use:**
```python
from questfoundry.state import WorkspaceManager

ws = WorkspaceManager.initialize(
    project_path=workspace_path,
    project_info=ProjectInfo(
        name=project_name,
        description=premise,
        metadata={"tone": tone, "length": length}
    )
)
```

**Impact:** CLI reinvents workspace management instead of using the battle-tested library implementation.

### 5. Quality Checks - Limited Implementation

**File:** `src/qf/commands/check.py`

**Lines 340-343:**
```python
console.print(
    "[dim]Additional quality bars (style, consistency, completeness) "
    "will be available once Layer 6 integration is complete.[/dim]\n"
)
```

**Current implementation:**
- 4 basic checks: schema validation, timeline consistency, codex coverage, hook resolution
- All implemented locally with basic logic

**questfoundry-py likely has:**
- Gatekeeper role with sophisticated validation
- Quality gate framework
- Lore consistency checking via `ConflictDetector`

### 6. Export Commands - Placeholders

**File:** `src/qf/commands/export.py`

**Line 68:** `# Simulate export (placeholder for actual Layer 6 integration)`

**Lines 72-78:** Creates fake files
```python
if format == "html":
    output_path.write_text("<html>...</html>")
    # Creates fake HTML
```

**File:** `src/qf/commands/bind.py`

**Line 68:** `# Simulate binding (placeholder for actual Layer 6 integration)`

**Lines 76-88:** Creates fake PDF/HTML/Markdown
```python
if format == "pdf":
    pdf_content = f"%PDF-1.4\n%Placeholder PDF for {snapshot_id}\n"
    output_path.write_bytes(pdf_content.encode())
```

**Should use:** BookBinder role from questfoundry-py role system

### 7. Generate Command - Partial Integration

**File:** `src/qf/commands/generate.py`

**Good news:** Lines 89-227 properly use questfoundry-py!
```python
from questfoundry.models import Artifact
from questfoundry.roles import RoleContext

role_registry = get_role_registry()
role = role_registry.get_role(role_name)
result = role.execute(context)
```

**Gap:** Generate commands work in isolation but aren't integrated into loop execution. Users can call `qf generate image` manually, but `qf run art-touchup` doesn't actually generate images.

### 8. Artifact Operations - Incomplete

**File:** `src/qf/commands/artifact.py`
- **Line 16:** `console.print("[yellow]Interactive artifact creation coming soon[/yellow]")`
- Entire command is a stub

**File:** `src/qf/commands/validate.py`
- **Lines 314-323:** Envelope validation is placeholder
- **Line 319:** `console.print("[yellow]Envelope validation coming soon[/yellow]")`

### 9. Status Command - Limited Introspection

**File:** `src/qf/commands/status.py`

**Lines 46-75:** Manually scans directories
```python
# Manually count files
hot_path = workspace / "hot"
artifact_count = sum(1 for f in hot_path.rglob("*.json"))
```

**Lines 77-81:**
```python
# Future sections (placeholder for Layer 6 integration)
console.print(
    "[dim]Additional status information (active roles, pending artifacts, TU history) "
    "will be available once Layer 6 integration is complete.[/dim]\n"
)
```

**Should use:**
```python
from questfoundry.state import WorkspaceManager

ws = WorkspaceManager(workspace_path)
artifacts = ws.list_hot_artifacts()
tu_history = ws.get_time_unit_history()
```

### 10. Provider Management - Hardcoded

**File:** `src/qf/commands/provider.py`

**Lines 16-25:** Hardcoded provider list
```python
KNOWN_PROVIDERS = {
    "openai": "OpenAI GPT models",
    "anthropic": "Anthropic Claude models",
    # ... etc
}
```

**Lines 113-116:**
```python
"[dim]Provider integration will be fully available "
"once Layer 6 is complete.[/dim]\n"
```

**Should use:**
```python
from questfoundry.providers import ProviderRegistry

registry = ProviderRegistry(config)
providers = registry.list_providers()
```

## "Layer 6" Misconception - Evidence

### References to "Layer 6" in Codebase

Found **30+ references** to "Layer 6" or "once Layer 6 arrives/is complete":

1. `EPIC_7_PLAN.md` - Multiple references to Layer 6 architecture
2. `docs/IMPLEMENTATION_PLAN.md` - 20+ references
3. `docs/LAYER_7_UPDATES_FOR_EPIC_7_8.md` - Architecture discussion
4. `src/qf/commands/run.py:114` - "questfoundry-py Showrunner in a future release"
5. `src/qf/commands/quickstart.py:98` - "actual Layer 6 Showrunner integration"
6. `src/qf/commands/quickstart.py:228` - "coming with Layer 6 integration"
7. `src/qf/commands/provider.py:115` - "once Layer 6 is complete"
8. `src/qf/commands/status.py:80` - "once Layer 6 integration is complete"
9. `src/qf/commands/check.py:342` - "once Layer 6 integration is complete"
10. `src/qf/commands/export.py:68,133` - Placeholder comments
11. `src/qf/commands/bind.py:68` - Placeholder comment

### The Reality

**Layer 6 (questfoundry-py) has ALWAYS been available:**

- v0.4.0 was already installed (just upgraded to v0.5.0)
- Has complete loop system, role system, state management
- Only thing "missing" was the Orchestrator, but loops can execute independently
- The CLI was waiting for something that already existed

### Why the Misconception?

Looking at `docs/QUESTFOUNDRY_PY_ANALYSIS.md` (which I found in the repo):

**Lines 1-6:**
```markdown
# questfoundry-py Integration Analysis

## Executive Summary

**Critical Finding:** The questfoundry-py roles for image and audio generation
are **NOT actually generating media files**. They only generate JSON specifications.
```

**Ah-ha moment:** Someone discovered that Illustrator and AudioProducer don't generate actual images/audio, only specs. They may have concluded "Layer 6 isn't ready" when actually it's a *design choice* - the roles generate specifications that downstream tools consume.

## Loop Definitions - CLI vs Library Comparison

### CLI (`loops.yml`) - 13 loops:
1. story-spark (SS) - Discovery
2. hook-harvest (HH) - Discovery
3. lore-deepening (LD) - Discovery
4. codex-expansion (CE) - Refinement
5. style-tuneup (ST) - Refinement
6. art-touchup (AT) - Asset
7. audio-pass (AP) - Asset
8. translation-pass (TP) - Asset
9. **gatecheck (GC) - Export** ⚠️
10. binding-run (BR) - Export
11. narration-dry-run (NDR) - Export
12. **post-mortem (PM) - Export** ⚠️
13. **archive-snapshot (AS) - Export** ⚠️

### Library (LoopRegistry) - 11 loops:
1. story_spark
2. hook_harvest
3. lore_deepening
4. codex_expansion
5. binding_run
6. style_tune_up
7. art_touch_up
8. audio_pass
9. translation_pass
10. narration_dry_run
11. full_production_run

### Differences:
- ❌ CLI has `gatecheck` - NOT in library
- ❌ CLI has `post-mortem` - NOT in library
- ❌ CLI has `archive-snapshot` - NOT in library
- ✅ Library has `full_production_run` - NOT in CLI YAML

### Name Mismatches:
- CLI: `style-tuneup` → Library: `style_tune_up`
- CLI: `art-touchup` → Library: `art_touch_up`
- CLI: `narration-dry-run` → Library: `narration_dry_run`

## Code Quality Issues

### Duplicate Implementations

1. **Schema validation** - Implemented locally instead of using `questfoundry.validators`
2. **Artifact types** - Hardcoded list instead of using library types
3. **Provider lists** - Hardcoded instead of using ProviderRegistry
4. **Workspace operations** - Manual file operations instead of WorkspaceManager

### Simulation Code (Should Delete)

1. `src/qf/commands/run.py` - Lines 119-177: All simulation
2. `src/qf/commands/quickstart.py` - Lines 95-126: Simulation function
3. `src/qf/commands/export.py` - Lines 68-78, 133-155: Fake exports
4. `src/qf/commands/bind.py` - Lines 68-88: Fake binding

### Misleading User Messages

Users running `qf run hook-harvest` think they're executing a real loop with AI agents, but they're actually just watching a progress bar with `time.sleep()` calls. This is a **critical UX issue**.

## Action Items - Priority Order

### 🔴 CRITICAL (Breaks thin wrapper principle)

1. **Remove simulation code from `run.py`**
   - Delete lines 119-177 (simulation)
   - Integrate `LoopRegistry` and loop execution
   - Remove "Layer 6" message on line 114

2. **Remove simulation from `quickstart.py`**
   - Delete `_simulate_loop_execution()` function
   - Integrate real loop execution
   - Remove misleading "Layer 6 integration coming" message

3. **Delete or reconcile `loops.yml`**
   - Option A: Delete and use LoopRegistry exclusively
   - Option B: Contribute missing loops to questfoundry-py
   - Ensure loop IDs match between CLI and library

### 🟡 HIGH (Core functionality)

4. **Integrate WorkspaceManager**
   - Replace manual workspace creation in `session.py`
   - Use WorkspaceManager in `init.py`
   - Use WorkspaceManager in `status.py` for artifact queries

5. **Fix export commands**
   - Integrate BookBinder role in `bind.py`
   - Remove placeholder export code in `export.py`

6. **Enhance quality checks**
   - Integrate Gatekeeper role
   - Use ConflictDetector for lore consistency
   - Remove "Layer 6" message

### 🟢 MEDIUM (Polish)

7. **Use ProviderRegistry**
   - Remove KNOWN_PROVIDERS hardcoded list
   - Query registry for available providers

8. **Implement artifact creation**
   - Remove "coming soon" message
   - Provide interactive artifact creation

9. **Implement envelope validation**
   - Remove "coming soon" message
   - Implement Layer 4 envelope validation

### 🔵 LOW (Nice-to-have)

10. **Centralize constants**
    - Move ARTIFACT_TYPES to questfoundry-py
    - Import from library instead of defining locally

11. **Use library validators**
    - Replace local schema validation with library functions
    - Simplify validation code

## Technical Debt Summary

| Category | Count | Impact |
|----------|-------|--------|
| Simulation functions | 4 | Critical - Users think work is happening |
| "Layer 6" messages | 10+ | High - Misleading information |
| Duplicate data structures | 3 | Medium - Maintenance burden |
| Placeholder commands | 5 | Medium - Incomplete functionality |
| Hardcoded constants | 4 | Low - Minor duplication |

## Recommendations

### Immediate Actions

1. **Remove ALL "Layer 6" references** - It's here, it's available, stop saying it's coming
2. **Remove ALL simulation code** - Replace with real library calls
3. **Update pyproject.toml** - Already done (v0.5.0)

### Architecture Alignment

This CLI should be a **thin wrapper** that:
- ✅ Provides beautiful terminal UI (Rich library)
- ✅ Handles user interaction (Typer, questionary)
- ✅ Manages CLI-specific configuration
- ❌ Does NOT simulate functionality
- ❌ Does NOT duplicate data structures
- ❌ Does NOT reimplement library features

### Communication

Update documentation to clarify:
- questfoundry-py (Layer 6) is complete and available
- Image/audio roles generate specifications by design
- CLI is being refactored to be a proper thin wrapper

## Test Coverage Gap

**Missing:** Integration tests with real questfoundry-py calls
**Current:** Unit tests with mocked questfoundry-py

**Recommendation:** Add integration test suite that:
1. Installs questfoundry-py
2. Runs real loop execution (with mocked LLM providers)
3. Verifies artifacts are created
4. Tests WorkspaceManager integration

## Conclusion

The questfoundry-cli repository contains extensive simulation code based on the incorrect assumption that questfoundry-py (Layer 6) was incomplete. In reality:

1. **questfoundry-py v0.5.0 is feature-complete** for core loop execution
2. **All necessary components exist**: LoopRegistry, RoleRegistry, WorkspaceManager, providers
3. **The CLI needs significant refactoring** to become a true thin wrapper
4. **User experience is currently misleading** - commands simulate work instead of doing it

The good news: The foundation is solid. The `generate` command shows that proper integration is possible. The CLI just needs to:
1. Remove simulation code
2. Wire up the library components
3. Delete misleading messages
4. Reconcile loop definitions

Estimated effort: **2-3 days** of focused refactoring to convert this from a simulation to a real CLI.

---

**Next Steps:**
1. Create GitHub issues for each integration gap
2. Prioritize critical items (loop execution, quickstart)
3. Plan refactoring sprints
4. Update documentation to remove Layer 6 references
5. Add integration tests
