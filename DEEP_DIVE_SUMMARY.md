# QuestFoundry CLI - Deep Dive Summary

**Date:** 2025-11-11
**Branch:** `claude/project-deep-dive-011CV2SD4HcVg8445vQ3uWjg`
**questfoundry-py version:** v0.5.0

---

## The Problem

The current CLI (4000+ lines) was built on outdated spec examples and **simulates** AI work instead of using the actual questfoundry-py library. Critical issues:

1. **134+ instances of simulation code** with `time.sleep()` calls
2. **No real loop execution** - everything is faked
3. **Duplicate data** - loops.yml duplicates LoopRegistry data
4. **Wrong architecture** - built for non-existent `Showrunner` orchestration class
5. **Missing integration** - interactive mode not wired up

**User's concern:** "The llm agent implementing this has been telling everything was fine and according to spec all the time, but apparently forgot about the spec."

---

## The Solution

**Complete rewrite** as a thin wrapper around questfoundry-py v0.5.0.

### What questfoundry-py Actually Provides

✅ **Orchestrator** - Coordinates loop execution (exists NOW)
✅ **WorkspaceManager** - Hot/cold storage management
✅ **LoopRegistry** - Access to 17 loops
✅ **RoleRegistry** - Access to 15 roles
✅ **ProviderRegistry** - LLM/image provider management
✅ **Gatekeeper** - Quality validation
✅ **Export System** - ViewGenerator, BookBinder, GitExporter
✅ **Human Callback System** - Interactive mode infrastructure

**Everything needed is already implemented in the library.**

---

## Documents Created

### 1. DEEP_DIVE_FINDINGS.md
- 15 critical integration gaps identified
- 134 instances of simulation/placeholder code catalogued
- Loop definition mismatches analyzed
- Technical debt quantified

### 2. REFACTOR_OR_REWRITE.md
- Cost-benefit analysis: Rewrite (6-8 days) vs Refactor (3-5 days)
- Recommendation: **Rewrite from scratch**
- Rationale: Clean foundation, no technical debt

### 3. SPEC_VS_REALITY.md
- Comparison of outdated spec examples vs actual implementation
- Key finding: Spec mentions `Showrunner` class that doesn't exist as orchestrator
- Reality: `Orchestrator` class coordinates, Showrunner is a Role
- Loop count mismatch explained (13 vs 17, different loops)

### 4. NEW_CLI_DESIGN.md
- Complete CLI design based on actual library
- Reality-based command structure
- 7-day implementation timeline
- Code examples showing proper integration
- ~40 lines vs 178 lines of simulation

### 5. IMPLEMENTATION_PLAN_V2.md
- Day-by-day breakdown of 7-day implementation
- Phase-by-phase approach with code examples
- Success criteria for each phase
- Testing strategy

### 6. INTERACTIVE_MODE_ANALYSIS.md ⭐
- **Critical oversight addressed:** Interactive mode integration
- **Key finding:** Showrunner coordinates ALL human interaction as "product manager"
- Complete research on human_callback system
- Integration path identified: CLI → Orchestrator → Showrunner → Roles
- Implementation approach documented

### 7. This Summary (DEEP_DIVE_SUMMARY.md)
- Executive overview of findings
- Implementation roadmap
- Next steps

---

## Key Technical Findings

### 1. Orchestrator Architecture

**Spec Example (Outdated):**
```python
# Layer 6/7 spec referenced this (doesn't exist):
showrunner = Showrunner(workspace, provider)
result = showrunner.execute_loop("story-spark")
```

**Actual Implementation (v0.5.0):**
```python
# This is how it actually works:
orchestrator = Orchestrator(workspace, provider_registry)
orchestrator.initialize(provider_name="openai")
result = orchestrator.execute_loop(
    loop_id="story-spark",
    project_id="my-project",
    config={}
)
```

### 2. Interactive Mode Integration

**The Spec's Intent:**
> "Showrunner should be responsible for all human interaction. It's the product manager so to speak"

**How It Works:**
1. Roles inherit `ask_human()` method from base class
2. Showrunner has `initialize_role_with_config(human_callback=...)` method
3. CLI provides callback via `config["human_callback"]`
4. Orchestrator passes to Showrunner
5. Showrunner distributes to all roles
6. All questions funnel through callback back to CLI

**Current State:**
- ✅ Infrastructure exists in library
- ⚠️  Orchestrator needs small enhancement to extract callback from config
- 📋 CLI needs to implement Rich UI callback

### 3. Loop Definitions

**Problem:** CLI had loops.yml duplicating library data

**Solution:** Delete loops.yml, use LoopRegistry:
```python
registry = LoopRegistry()
loops = registry.list_loops()  # Returns 17 LoopMetadata objects
for loop in loops:
    console.print(f"{loop.loop_id}: {loop.description}")
```

### 4. Workspace Management

**Problem:** CLI manually created directories/files

**Solution:** Use WorkspaceManager:
```python
ws = WorkspaceManager("./my-adventure")
ws.init_workspace(name="Dragon Quest", author="Alice")
ws.save_hot_artifact(artifact)
ws.promote_to_cold("HOOK-001")
```

---

## Implementation Roadmap

### Phase 1: Foundation (Day 1)
**Goal:** Minimal working prototype

Commands:
- `qf init` → WorkspaceManager.init_workspace()
- `qf status` → WorkspaceManager queries
- `qf config` → YAML file operations

**No AI calls yet. Just project management.**

### Phase 2: Loop Execution (Days 2-3) ⭐ CRITICAL
**Goal:** Real loop execution with Orchestrator

Commands:
- `qf loop run <loop>` → Orchestrator.execute_loop()
- `qf loop auto <goal>` → Orchestrator.select_loop() + execute
- `qf loop list` → LoopRegistry.list_loops()

**This is the key integration. Everything else is formatting.**

### Phase 3: Artifact Operations (Day 4)
**Goal:** Manage artifacts

Commands:
- `qf list hooks/canon/codex/all`
- `qf show <artifact-id>`
- `qf search <query>`
- `qf promote/demote <artifact-id>`

### Phase 4: Quality & Export (Day 5)
**Goal:** Validation and export

Commands:
- `qf check` → Gatekeeper.run_gatecheck()
- `qf export view` → ViewGenerator.generate_view()
- `qf bind` → BookBinder.render_html()

### Phase 5: Polish (Days 6-7)
**Goal:** Professional UX

- Rich formatting for all outputs
- Interactive mode (`--interactive` flag)
- Shell completion
- Comprehensive documentation
- Integration tests

---

## Interactive Mode Implementation

### What Needs to Happen

**Option A: Enhance Orchestrator (Recommended)**

Modify questfoundry-py:
```python
# In Orchestrator.execute_loop()
def execute_loop(self, loop_id, project_id, artifacts=None, config=None):
    # Extract human_callback from config
    human_callback = (config or {}).get("human_callback")

    # Get showrunner
    showrunner = self.role_registry.get_role("showrunner")

    # Let Showrunner initialize roles WITH callback
    role_instances = {}
    for role_name in required_roles:
        role_class = self.role_registry._roles[role_name]
        role_instances[role_name] = showrunner.initialize_role_with_config(
            role_class=role_class,
            registry=self.provider_registry,
            human_callback=human_callback,  # ← Distributed by Showrunner
        )

    # Continue with loop execution...
```

**Option B: CLI Workaround**

Use existing infrastructure:
```python
# In qf/commands/loop.py
def run(loop_id: str, interactive: bool = False):
    orchestrator = Orchestrator(ws, provider_registry)
    orchestrator.initialize(provider_name="openai")

    loop_config = {}
    if interactive:
        from ..interactive.callback import cli_interactive_callback
        loop_config["human_callback"] = cli_interactive_callback

    result = orchestrator.execute_loop(
        loop_id=loop_id,
        project_id=project_id,
        config=loop_config  # ← Callback passed here
    )
```

### CLI Callback Implementation

```python
# src/qf/interactive/callback.py

from typing import Any
from rich.console import Console
from rich.panel import Panel
import questionary

console = Console()

def cli_interactive_callback(question: str, context: dict[str, Any]) -> str:
    """CLI callback for agent-to-human questions."""
    role = context.get("role", "Agent")
    suggestions = context.get("suggestions", [])

    # Display question in Rich panel
    console.print()
    console.print(
        Panel(
            f"[bold cyan]{question}[/bold cyan]",
            title=f"[{role}] Question",
            border_style="cyan",
        )
    )

    # Use questionary for better UX
    if suggestions:
        answer = questionary.select(
            "Choose an option:",
            choices=[*suggestions, "Custom answer..."]
        ).ask()

        if answer == "Custom answer...":
            answer = questionary.text("Your answer:").ask()

        return answer
    else:
        return questionary.text("Your answer:").ask()
```

---

## Success Criteria

### Must Have
- [x] Deep understanding of questfoundry-py v0.5.0 architecture
- [x] Clear documentation of gaps in current CLI
- [x] Reality-based design using actual library
- [x] 7-day implementation plan
- [x] Interactive mode integration path identified
- [ ] `qf init` creates real workspace with WorkspaceManager
- [ ] `qf loop run <loop>` executes real AI loop via Orchestrator
- [ ] `qf list` queries real workspace artifacts
- [ ] `qf check` runs real Gatekeeper validation
- [ ] NO simulation code anywhere
- [ ] NO duplicate data files

### Should Have
- [ ] `qf loop auto <goal>` - Orchestrator selects loop
- [ ] `qf loop run --interactive` - Agent asks questions
- [ ] Rich formatting for all outputs
- [ ] Shell completion
- [ ] Comprehensive tests

### Nice to Have
- [ ] `qf promote/demote` - Hot/cold management
- [ ] `qf search` - Query artifacts
- [ ] Progress bars during loop execution
- [ ] TUI mode (future)

---

## Next Steps

### 1. Decision Point: Orchestrator Enhancement

**Question:** Should we enhance Orchestrator in questfoundry-py to wire up interactive mode cleanly?

**Options:**
- A) Submit PR to questfoundry-py with Orchestrator enhancement (cleaner, proper integration)
- B) Work around in CLI using config workaround (faster, less ideal)

**Recommendation:** Option A - proper integration benefits all users of the library.

### 2. Begin Implementation

Once decision made, start Phase 1:

```bash
# Archive old implementation
mv src/qf/commands src/qf/commands_old

# Start fresh
mkdir -p src/qf/commands
mkdir -p src/qf/interactive
mkdir -p src/qf/formatting
mkdir -p src/qf/utils

# Implement foundation
# Day 1: init, status, config
# Day 2-3: loop execution (THE KEY)
# Day 4: artifact operations
# Day 5: quality & export
# Day 6-7: polish & interactive mode
```

### 3. Testing Strategy

- Unit tests for each command
- Integration tests with mock provider
- End-to-end tests with real AI (optional, expensive)
- Interactive mode tests with mock questions

---

## Conclusion

**Current CLI:** Built on wrong assumptions, 4000+ lines of simulation

**New CLI:** Thin wrapper, ~1000 lines, real functionality

**The library does the work. The CLI just shows it to users.**

That's what "thin wrapper" actually means.

**All analysis complete. Ready to implement.**

---

## Files in This Analysis

1. `DEEP_DIVE_FINDINGS.md` - Problems identified
2. `REFACTOR_OR_REWRITE.md` - Decision framework
3. `SPEC_VS_REALITY.md` - Spec vs implementation
4. `NEW_CLI_DESIGN.md` - Complete new design
5. `IMPLEMENTATION_PLAN_V2.md` - 7-day plan
6. `INTERACTIVE_MODE_ANALYSIS.md` - Interactive mode research
7. `DEEP_DIVE_SUMMARY.md` - This document

**All committed to:** `claude/project-deep-dive-011CV2SD4HcVg8445vQ3uWjg`
