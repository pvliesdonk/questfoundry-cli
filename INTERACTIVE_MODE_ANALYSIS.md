# Interactive Mode - Analysis & Integration

**Date:** 2025-11-11
**Issue:** Interactive mode was not fully addressed in NEW_CLI_DESIGN.md
**Status:** ✅ Research complete - Implementation path identified

---

## Executive Summary

**Key Finding:** Showrunner coordinates ALL human interaction (as "product manager").

**How It Works:**
1. questfoundry-py v0.5.0 has complete `human_callback` infrastructure
2. Roles inherit `ask_human()` method to ask questions
3. Showrunner has `initialize_role_with_config(human_callback=...)` to distribute callback to roles
4. CLI provides Rich UI callback via `config["human_callback"]`
5. All agent questions funnel through this callback back to CLI

**Implementation Status:**
- ✅ Library infrastructure exists (roles/human_callback.py, roles/base.py, roles/showrunner.py)
- ✅ Spec defines interactive mode (spec/07-ui/README.md:198-254)
- ⚠️  Orchestrator needs small enhancement to wire it up
- 📋 CLI needs to implement Rich callback and `--interactive` flag

**Timeline:** Can be implemented in Phase 2 (loop execution) alongside basic loop functionality.

---

## What Interactive Mode Is

From the spec (spec/07-ui/README.md:199-253), interactive mode allows **AI agents to ask the user questions during loop execution**, enabling conversational collaboration.

**Example workflow:**
```
User: qf loop run hook-harvest --interactive

[Lore Weaver]: I'm analyzing your premise. I see potential for both
cosmic horror and psychological thriller elements.

Question: Should the supernatural elements be:
  a) Ambiguous (possibly explained naturally)
  b) Clearly supernatural
  c) Something else?

Your answer: Let's keep it ambiguous until midgame

[Lore Weaver]: Perfect! I'll seed hooks that work both ways...
```

---

## What questfoundry-py v0.5.0 Provides

### ✅ Human Callback System Exists

**File:** `src/questfoundry/roles/human_callback.py`

```python
# Type definition
HumanCallback = Callable[[str, dict[str, Any]], str]

# Built-in implementations
def default_human_callback(question: str, context: dict[str, Any]) -> str:
    """Simple stdin prompt (reference implementation)"""
    print(f"\n[{role}] {question}")
    if suggestions:
        print("\nSuggestions:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    return input("Your answer: ")

def batch_mode_callback(question: str, context: dict[str, Any]) -> str:
    """Auto-responds for non-interactive mode"""
    suggestions = context.get("suggestions", [])
    return suggestions[0] if suggestions else ""
```

### ✅ Roles Support Human Callbacks

**File:** `src/questfoundry/roles/base.py`

```python
class Role(ABC):
    def __init__(
        self,
        provider: TextProvider,
        human_callback: HumanCallback | None = None,  # ← HERE
        # ... other params
    ):
        self.human_callback = human_callback or batch_mode_callback

    def ask_human(
        self,
        question: str,
        suggestions: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Ask human a question (interactive mode).

        Args:
            question: The question to ask
            suggestions: Suggested answers
            context: Additional context

        Returns:
            Human's response
        """
        callback_context = {
            "role": self.role_name,
            "question": question,
            "suggestions": suggestions or [],
            "context": context or {},
        }

        return self.human_callback(question, callback_context)
```

**Roles can call `self.ask_human()` at any point during execution.**

### ❓ Integration with Orchestrator/Loops

**Question:** Does the Orchestrator/RoleRegistry allow passing human_callback when creating roles?

Looking at the code:
- `RoleRegistry.get_role()` signature - need to check
- `Orchestrator.execute_loop()` - doesn't show human_callback parameter
- Loop execution flow - need to verify

**Current status:** The infrastructure exists, but I need to verify the integration path.

---

## How CLI Should Support Interactive Mode

### Design Approach

```python
# Non-interactive (default)
qf loop run hook-harvest
→ Roles use batch_mode_callback (auto-responds)

# Interactive
qf loop run hook-harvest --interactive
→ Roles use CLI-provided callback that displays Rich UI
```

### Implementation Strategy

#### 1. Create Rich Interactive Callback

**File:** `src/qf/interactive/callback.py`

```python
"""Interactive callback for CLI."""
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import questionary

console = Console()

def cli_interactive_callback(question: str, context: dict[str, Any]) -> str:
    """
    CLI callback for agent-to-human questions.

    Displays questions in Rich UI and collects responses.

    Args:
        question: The question to ask
        context: Context including role, suggestions, etc.

    Returns:
        Human's response
    """
    role = context.get("role", "Agent")
    suggestions = context.get("suggestions", [])

    # Display in Rich panel
    console.print()
    console.print(
        Panel(
            f"[bold cyan]{question}[/bold cyan]",
            title=f"[{role}] Question",
            border_style="cyan",
        )
    )

    # Use questionary for better UX if suggestions provided
    if suggestions:
        answer = questionary.select(
            "Choose an option (or type custom response):",
            choices=[*suggestions, "Custom answer..."]
        ).ask()

        if answer == "Custom answer...":
            answer = questionary.text("Your answer:").ask()

        return answer
    else:
        # Free-form response
        return questionary.text(
            "Your answer:",
            multiline=False
        ).ask()
```

#### 2. Pass Callback via Config (CORRECT APPROACH)

Based on research, the clean integration path is through Orchestrator config:

```python
# In qf/commands/loop.py

from questfoundry.orchestrator import Orchestrator
from questfoundry.state import WorkspaceManager
from questfoundry.providers.config import ProviderConfig
from questfoundry.providers.registry import ProviderRegistry

def run(loop_id: str, interactive: bool = False):
    # Load workspace
    ws = WorkspaceManager(find_workspace())

    # Load providers
    config = ProviderConfig.from_file(ws.path / ".questfoundry" / "config.yml")
    provider_registry = ProviderRegistry(config)

    # Create orchestrator
    orchestrator = Orchestrator(ws, provider_registry)
    orchestrator.initialize(provider_name="openai")

    # Get project ID
    project_id = ws.get_project_info().project_id

    # Prepare loop config
    loop_config = {}
    if interactive:
        from ..interactive.callback import cli_interactive_callback
        loop_config["human_callback"] = cli_interactive_callback

    # Execute loop with config
    result = orchestrator.execute_loop(
        loop_id=loop_id,
        project_id=project_id,
        config=loop_config  # ← Callback passed here
    )

    return result
```

**How it works:**
1. CLI creates `cli_interactive_callback` function
2. Passes it in `config["human_callback"]`
3. Orchestrator extracts callback from config
4. Showrunner uses `initialize_role_with_config()` to create roles
5. Each role receives the callback and can call `self.ask_human()`
6. Questions route through callback back to CLI
7. CLI displays Rich UI and collects user response
8. Response returns to role, which continues execution

**Note:** This requires a small enhancement to Orchestrator (see "Option A" in Research section below).

### User Experience

```bash
$ qf loop run hook-harvest --interactive

Executing: Hook Harvest
⠋ Running loop...

┌─ [Lore Weaver] Question ────────────────────────┐
│ I'm analyzing your premise about a coastal      │
│ mystery. Should the supernatural elements be:   │
│                                                  │
│ a) Ambiguous (possibly natural explanations)    │
│ b) Clearly supernatural                          │
│ c) Something else?                               │
└──────────────────────────────────────────────────┘

? Choose an option:
  ❯ Ambiguous (possibly natural explanations)
    Clearly supernatural
    Custom answer...

Your answer: Ambiguous

[Lore Weaver]: Perfect! Creating hooks that work both ways...

✓ Hook Harvest complete!
Duration: 00:03:42
Artifacts created: 5
```

---

## Questions Answered Through Research

### 1. Does RoleRegistry support human_callback parameter?

**Answer:** No, but it doesn't need to.

- `RoleRegistry.get_role()` does NOT accept `human_callback` (confirmed in registry.py:142-149)
- However, Showrunner has `initialize_role_with_config()` that DOES accept it (showrunner.py:393-463)
- The correct path: Orchestrator → Showrunner → Roles (not Orchestrator → RoleRegistry → Roles)

### 2. Does Orchestrator/Loop pass human_callback to roles?

**Answer:** Not yet, but the infrastructure exists.

- `Orchestrator.execute_loop()` accepts `config` dict (orchestrator.py:190)
- `LoopContext` stores this config (loops/base.py:103)
- Currently Orchestrator uses RoleRegistry.get_role() directly (orchestrator.py:227-231)
- **Need enhancement:** Extract `human_callback` from config and route through Showrunner

### 3. Which roles actually use ask_human()?

**Answer:** All roles CAN, implementation-dependent.

- All roles inherit from `Role` base class which has `ask_human()` method (roles/base.py)
- Spec examples show Lore Weaver asking questions (spec/07-ui/README.md:214-226)
- Spec says questions arise from: "Ambiguity that blocks progress, forking choices, facts" (spec/05-prompts/_shared/human_interaction.md:17-20)
- In practice: Lore Weaver, Scene Smith, Plotwright likely to ask questions
- Showrunner coordinates all interactions as "product manager"

### 4. Are there examples/tests of interactive mode?

**Answer:** Spec has examples, implementation is partial.

- Spec shows interactive mode workflow (spec/07-ui/README.md:198-244)
- human_callback infrastructure exists (roles/human_callback.py)
- Roles support ask_human() (roles/base.py)
- **Missing piece:** Orchestrator doesn't wire it up yet

---

## Action Items

### Research (COMPLETED ✅)

- [x] Read `RoleRegistry` implementation fully
- [x] Trace `Orchestrator.execute_loop()` to see role creation
- [x] Check spec for interactive mode examples
- [x] Verify which roles use `ask_human()`
- [x] Understand Showrunner's coordination role

### Library Enhancement (questfoundry-py)

**Optional but recommended:**
- [ ] Enhance `Orchestrator.execute_loop()` to extract `human_callback` from config
- [ ] Modify role instantiation to use `showrunner.initialize_role_with_config()`
- [ ] Add integration test for interactive mode

**Alternative (CLI workaround):**
- [ ] CLI can work around by passing callback via config
- [ ] Relies on existing `showrunner.initialize_role_with_config()` method

### CLI Implementation

- [ ] Create `src/qf/interactive/callback.py` with Rich UI callback
- [ ] Add `--interactive` flag to `qf loop run` command
- [ ] Pass callback via `config["human_callback"]`
- [ ] Display agent questions with Rich panels
- [ ] Collect responses with questionary
- [ ] Document interactive mode in CLI README

### Testing

- [ ] Unit test: CLI callback UI formatting
- [ ] Integration test: Mock role asking questions
- [ ] End-to-end test: `qf loop run --interactive`
- [ ] Test multi-turn conversations
- [ ] Test with/without suggestions

---

## Updated CLI Design

### Commands

```bash
# Batch mode (default) - roles auto-respond
qf loop run hook-harvest

# Interactive mode - roles can ask questions
qf loop run hook-harvest --interactive
qf loop run lore-deepening --interactive

# Auto-select loop (interactive by default?)
qf loop auto "Add a dragon" --interactive
```

### Config Options

```yaml
# .questfoundry/config.yml

# Interactive mode defaults
ui:
  interactive_by_default: false  # Or true for always-on
  interactive_timeout: 300  # Auto-proceed after 5min if no response
  use_suggestions: true  # Show suggestions from roles
```

---

## Integration Priority

**Priority:** HIGH (after basic loop execution works)

**Rationale:**
- Interactive mode is a key UX differentiator
- Library already supports it via human_callback
- CLI just needs to wire it up
- Relatively straightforward once basic loops work

**Timeline:**
- Phase 2 Day 3: Add basic interactive support
- Phase 5 Day 6: Polish interactive UX

---

## Notes

- The `default_human_callback` in questfoundry-py is a **reference implementation**
- Production CLI should use Rich UI for better experience
- Consider questionary for multi-choice questions
- Consider timeout mechanism for batch-fallback
- Log all questions/answers for audit trail

---

## Research Complete: How It Actually Works

After studying questfoundry-py v0.5.0 implementation:

### Current Architecture

**Role Support (✅ Works):**
- `Role.__init__()` accepts `human_callback` parameter
- Roles call `self.ask_human(question, suggestions)` to interact
- Default is `batch_mode_callback` (auto-responds)

**Showrunner's Job:**
- Showrunner has `initialize_role_with_config(role_class, registry, human_callback=...)` method
- This method creates role instances WITH the human_callback
- Located: `/tmp/questfoundry-py/src/questfoundry/roles/showrunner.py:393-463`

**Current Gap:**
- `Orchestrator.execute_loop()` uses `RoleRegistry.get_role()` to create roles
- `RoleRegistry.get_role()` does NOT accept or pass `human_callback`
- Roles are instantiated WITHOUT human interaction capability

**The Spec's Intent:**
> "Showrunner should be responsible for all human interaction. It's the product manager so to speak"

This means:
1. Showrunner coordinates all questions from other roles
2. CLI provides human_callback to Showrunner
3. Showrunner distributes callback to roles it initializes
4. All agent questions funnel through Showrunner's coordination

### The Right Integration Path

**Option A: Extend Orchestrator to support human_callback (RECOMMENDED)**

The Orchestrator should be enhanced to:
1. Accept `human_callback` in config
2. Pass it to Showrunner
3. Showrunner uses `initialize_role_with_config()` to create roles with the callback

```python
# In Orchestrator.execute_loop()

def execute_loop(
    self,
    loop_id: str,
    project_id: str,
    artifacts: list[Artifact] | None = None,
    config: dict[str, Any] | None = None,
) -> LoopResult:
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
            human_callback=human_callback,  # ← Showrunner distributes to all roles
        )

    # Rest of loop execution...
```

**Option B: Extend RoleRegistry to accept human_callback (ALTERNATIVE)**

Add human_callback parameter to RoleRegistry.get_role():

```python
# In RoleRegistry.get_role()

def get_role(
    self,
    name: str,
    provider: TextProvider | None = None,
    provider_name: str | None = None,
    human_callback: HumanCallback | None = None,  # ← Add this
) -> Role:
    # ...existing provider setup...

    instance = role_class(
        provider=provider,
        spec_path=self.spec_path,
        config=config,
        human_callback=human_callback,  # ← Pass through
    )
```

**Recommendation:** Option A aligns better with spec's intent that Showrunner coordinates human interaction.

## Status

**Research:** ✅ COMPLETE

**Findings:**
- Roles support human_callback (via base.py)
- Showrunner has `initialize_role_with_config()` method designed for this
- Orchestrator currently bypasses this and uses RoleRegistry directly
- Need to enhance Orchestrator to route through Showrunner for interactive mode

**Implementation:** Ready to proceed

**Priority:** HIGH - Include in Phase 2 (loop execution) design
