# Spec vs Reality Analysis

**Date:** 2025-11-11
**questfoundry-py version:** 0.5.0
**Spec version:** spec@a7a1649 (2025-10-31)

## Executive Summary

The specs in `spec/06-libraries` and `spec/07-ui` were written **in parallel** with the implementation, and are now **partially outdated**. The library (questfoundry-py) evolved differently than specified, primarily around loop orchestration.

### Key Differences

| Spec Says | Reality (v0.5.0) | Status |
|-----------|------------------|--------|
| `questfoundry.orchestration.Showrunner` | No `orchestration` module | ❌ Spec outdated |
| Loop orchestration via Showrunner | Loop orchestration via `Loop.execute()` | ✅ Works differently |
| `questfoundry.protocol.ProtocolClient` | ✅ Exists | ✅ Spec correct |
| `questfoundry.state.WorkspaceManager` | ✅ Exists | ✅ Spec correct |
| `questfoundry.providers.ProviderRegistry` | ✅ Exists | ✅ Spec correct |
| `questfoundry.roles.RoleRegistry` | ✅ Exists | ✅ Spec correct |
| 13 loops in spec | 11 loops in library | ⚠️ Mismatch |

---

## Detailed Comparison

### 1. Loop Orchestration (MAJOR DIFFERENCE)

#### Spec Says (spec/07-ui/README.md:590-602)

```python
from questfoundry.orchestration import Showrunner
from questfoundry import ProtocolClient

def run_loop(loop_name: str, interactive: bool = False):
    client = ProtocolClient(workspace=current_project)
    showrunner = Showrunner(client, interactive=interactive)

    # Execute loop
    result = showrunner.run_loop(loop_name)

    # Display results
    display_loop_summary(result)
```

#### Reality (v0.5.0)

```python
from questfoundry.loops import LoopRegistry, LoopContext
from questfoundry.state import WorkspaceManager

def run_loop(loop_name: str):
    # Get loop from registry
    registry = LoopRegistry()
    loop_metadata = registry.list_loops()  # Returns list of LoopMetadata

    # Find specific loop
    # (Note: No .get_loop() method exists, must iterate list)

    # Execute loop directly
    loop = Loop(...)  # Need to figure out construction
    result = loop.execute(context)
```

**Implications:**
- ❌ No `Showrunner` class exists
- ✅ `Loop.execute()` method exists
- ⚠️ Need to understand how to properly instantiate and execute loops
- ⚠️ LoopRegistry doesn't have `.get_loop(id)` method, only `.list_loops()`

---

### 2. Loop Definitions

#### Spec Loops (from spec/00-north-star/LOOPS/)

13 loops defined:
1. story_spark
2. hook_harvest
3. lore_deepening
4. codex_expansion
5. style_tune_up
6. art_touch_up
7. audio_pass
8. translation_pass
9. **gatecheck** ⚠️
10. binding_run
11. narration_dry_run
12. **post_mortem** ⚠️
13. **archive_snapshot** ⚠️

#### Reality (v0.5.0 LoopRegistry)

11 loops available:
1. story_spark ✅
2. hook_harvest ✅
3. lore_deepening ✅
4. codex_expansion ✅
5. binding_run ✅
6. style_tune_up ✅
7. art_touch_up ✅
8. audio_pass ✅
9. translation_pass ✅
10. narration_dry_run ✅
11. **full_production_run** (not in spec)

#### Mismatches

**Missing from library:**
- gatecheck (GC)
- post_mortem (PM)
- archive_snapshot (AS)

**Extra in library:**
- full_production_run (not in spec)

**Action:** Either add missing loops to library OR update spec to match reality

---

### 3. WorkspaceManager (MATCHES SPEC)

#### Spec Says (spec/06-libraries/README.md:101-115)

```
workspace/
  my-adventure.qfproj       # SQLite file (Cold SoT)
  .questfoundry/
    config.yml              # LLM providers, role config
    hot/                    # File-based hot workspace
      hooks/
      canon/
      artifacts/
    cache/                  # LLM response cache
    sessions/               # Active role sessions
```

#### Reality (v0.5.0)

```python
from questfoundry.state import WorkspaceManager

ws = WorkspaceManager.init_workspace(path)

# Available methods:
ws.save_hot_artifact()
ws.list_hot_artifacts()
ws.save_cold_artifact()
ws.list_cold_artifacts()
ws.save_tu()
ws.list_tus()
ws.get_project_info()
ws.save_project_info()
ws.save_snapshot()
ws.list_snapshots()
```

**Status:** ✅ Matches spec closely

---

### 4. ProviderRegistry (MATCHES SPEC)

#### Spec Says (spec/06-libraries/README.md:158-203)

```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
```

#### Reality (v0.5.0)

```python
from questfoundry.providers import ProviderRegistry, ProviderConfig

# Exists and matches spec architecture
```

**Status:** ✅ Matches spec

---

### 5. RoleRegistry (MATCHES SPEC)

#### Spec Says (spec/06-libraries/README.md:206-246)

```python
class RoleSession:
    role: str
    tu_context: str
    conversation_history: List[Envelope]

    def send_message(self, envelope: Envelope) -> Envelope:
        pass

    def ask_human(self, question: str, **kwargs) -> str:
        pass
```

#### Reality (v0.5.0)

```python
from questfoundry.roles import RoleRegistry, RoleContext, RoleResult

# Available and functional
# Used successfully in generate.py commands
```

**Status:** ✅ Matches spec (though may not have full Session management)

---

### 6. ProtocolClient (EXISTS)

#### Spec Says (spec/06-libraries/README.md:256-286)

```python
from questfoundry.protocol import ProtocolClient, Envelope

client = ProtocolClient(workspace="./my-adventure.qfproj")
response = client.send(envelope)
```

#### Reality (v0.5.0)

```python
from questfoundry.protocol import ProtocolClient

# Exists but unsure of exact API
```

**Status:** ✅ Exists, need to verify API

---

## What Works in Current CLI (Accidentally Correct)

### ✅ `qf generate` Commands

**File:** `src/qf/commands/generate.py`

**Lines 89-227:** Actually uses questfoundry-py correctly!

```python
from questfoundry.models import Artifact
from questfoundry.roles import RoleContext

role_registry = get_role_registry()
role = role_registry.get_role(role_name)
result = role.execute(context)
```

**Why it works:** This was integrated in Epic 6, AFTER learning how the library actually works.

---

## What's Broken in Current CLI

### ❌ `qf run` - Uses Simulation

**File:** `src/qf/commands/run.py:119-177`

```python
# All fake!
time.sleep(0.2)
progress_tracker.start_step("Context initialization", "Lore Weaver")
time.sleep(0.3)
```

**Should be:**
```python
from questfoundry.loops import LoopRegistry, LoopContext

registry = LoopRegistry()
# TODO: Figure out how to get and execute loop
```

---

### ❌ `qf quickstart` - Uses Simulation

**File:** `src/qf/commands/quickstart.py:95-126`

```python
def _simulate_loop_execution(loop_name: str) -> None:
    """Simulate loop execution with placeholder."""
    time.sleep(1.5)
```

---

### ❌ `data/loops.yml` - Duplicates Library Data

**File:** `src/qf/data/loops.yml`

83 lines defining 13 loops that should come from `LoopRegistry.list_loops()`

---

## Key Questions to Answer

### 1. How do you actually execute a loop?

**From exploration:**
```python
from questfoundry.loops import Loop

# Loop has .execute() method
# But how do you get a Loop instance from LoopRegistry?
registry = LoopRegistry()
loops = registry.list_loops()  # Returns list of LoopMetadata

# No .get_loop(id) method visible
# Must be a different pattern
```

**Need to investigate:**
- How to instantiate a Loop
- What LoopContext contains
- How Loop.execute() is called
- What LoopResult contains

---

### 2. Is there any orchestration, or are loops independent?

**Hypothesis based on loop metadata:**
- Each loop has `entry_conditions` and `exit_conditions`
- Some loops reference outputs of other loops
- Example: "Hook Harvest" → entry: "After Story Spark or drafting burst"

**Questions:**
- Is there a coordinator that chains loops?
- Or does user manually run loops in sequence?
- What does `full_production_run` loop do?

---

### 3. How does interactive mode work?

**Spec says (spec/07-ui/README.md:246-254):**
```python
def ask_human(self, question: str, **kwargs) -> str:
    # Creates human.question intent (Layer 4)
    # Waits for human.response
    # Response sent as human.response intent
```

**Questions:**
- Does RoleContext support this?
- How does CLI intercept and respond?
- Is there a callback mechanism?

---

## Recommendations for Clean CLI Rebuild

### Phase 1: Investigation (1 day)

**Tasks:**
1. Study questfoundry-py source code directly (not just API):
   - Read `questfoundry/loops/base.py` - understand Loop class
   - Read `questfoundry/loops/registry.py` - understand how loops are registered
   - Read `questfoundry/state/workspace.py` - understand WorkspaceManager
   - Read examples or tests in questfoundry-py repo

2. Write exploration scripts:
   ```python
   # explore_loop_execution.py
   from questfoundry.loops import LoopRegistry
   from questfoundry.state import WorkspaceManager

   # Try to execute a simple loop
   registry = LoopRegistry()
   # ... figure out the pattern
   ```

3. Document actual API in `QUESTFOUNDRY_PY_API.md`

---

### Phase 2: Spec Update (0.5 days)

**Tasks:**
1. Update `spec/07-ui/README.md` example code to match reality
2. Document differences between spec and implementation
3. Note: Spec can remain aspirational, but examples must work

---

### Phase 3: CLI Rebuild (4-6 days)

**Day 1: Core Infrastructure**
- `qf init` using `WorkspaceManager.init_workspace()`
- `qf status` using `WorkspaceManager.list_*()` methods
- Real integration, no simulation

**Day 2: Loop Execution**
- `qf run <loop>` using actual Loop.execute()
- Real progress tracking from loop execution events
- Remove all time.sleep() calls

**Day 3: Quickstart**
- `qf quickstart` orchestrating real loops
- Remove simulation
- Real artifact creation

**Day 4: Refinement**
- `qf list`, `qf show` using WorkspaceManager
- `qf check` using library validation
- Polish output formatting

**Day 5-6: Advanced Features**
- Interactive mode (if supported by library)
- Export/bind using BookBinder role
- Shell completion

---

## Critical Path Forward

1. **READ questfoundry-py SOURCE CODE** - Don't trust specs, read actual code
2. **Write exploration scripts** - Prove you can execute loops before building CLI
3. **Minimal prototype** - Just `qf init` and `qf run` with REAL library calls
4. **Then build the rest** - Once core pattern is proven

---

## Files to Reference from Old CLI

Keep these patterns (they're good):
- ✅ `src/qf/formatting/` - Rich formatting utilities
- ✅ `src/qf/interactive/prompts.py` - Questionary prompt patterns
- ✅ `src/qf/completions/` - Shell completion structure
- ✅ `tests/` - Test infrastructure setup

Delete or replace:
- ❌ `src/qf/data/loops.yml` - Use LoopRegistry
- ❌ `src/qf/commands/run.py` - Rewrite with real execution
- ❌ `src/qf/commands/quickstart.py` - Rewrite with real loops
- ❌ All time.sleep() calls

---

## Next Steps

### Option A: Study First (Recommended)

1. Clone questfoundry-py locally: `git clone questfoundry-py`
2. Read source code for 2-4 hours
3. Write working exploration script that executes a loop
4. Document findings in `QUESTFOUNDRY_PY_API.md`
5. **Then** start CLI rebuild with confidence

### Option B: Prototype First

1. Try to write minimal `qf run` that actually works
2. Learn by trial and error
3. Risk: Might build on wrong assumptions again

**Recommendation:** Option A - Study first, build second

---

## Conclusion

The specs are **good guides** but **outdated in key areas**:
- ✅ Overall architecture is correct (thin wrapper principle)
- ✅ Commands and UX design are sound
- ❌ Code examples reference non-existent `Showrunner`
- ❌ Loop orchestration pattern is different in reality

**The library (questfoundry-py v0.5.0) is fully functional**, just evolved differently than spec predicted.

**The CLI rebuild should:**
1. Study the actual library first
2. Ignore outdated spec examples
3. Build thin wrappers around real library functions
4. Port good UX patterns from old CLI
5. Test with real library integration

**Estimated rebuild time:** 5-7 days (1 day study + 4-6 days building)
