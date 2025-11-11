# Interactive Mode - Analysis & Integration

**Date:** 2025-11-11
**Issue:** Interactive mode was not fully addressed in NEW_CLI_DESIGN.md

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

#### 2. Pass Callback to Orchestrator/Roles

**Option A: Via RoleRegistry (if supported)**

```python
# In qf/commands/loop.py

def run(loop_id: str, interactive: bool = False):
    ws = get_workspace_manager()
    provider_registry = get_provider_registry()

    # Create human callback
    human_callback = None
    if interactive:
        from ..interactive.callback import cli_interactive_callback
        human_callback = cli_interactive_callback

    # Create role registry with callback
    role_registry = RoleRegistry(
        provider_registry,
        human_callback=human_callback  # ← Need to verify this works
    )

    # Create orchestrator with role registry
    orchestrator = Orchestrator(
        workspace=ws,
        provider_registry=provider_registry,
        role_registry=role_registry
    )

    orchestrator.initialize(provider_name="openai")
    result = orchestrator.execute_loop(loop_id)
```

**Option B: Via Loop Context (if supported)**

```python
# If loops support human_callback in context

def run(loop_id: str, interactive: bool = False):
    # ... setup

    config = {}
    if interactive:
        from ..interactive.callback import cli_interactive_callback
        config["human_callback"] = cli_interactive_callback

    result = orchestrator.execute_loop(loop_id, config=config)
```

**Option C: Monkey-patch roles (fallback)**

```python
# If no direct support, set callback on role instances

def run(loop_id: str, interactive: bool = False):
    # ... setup orchestrator

    if interactive:
        from ..interactive.callback import cli_interactive_callback

        # Get all roles and set callback
        for role_name in orchestrator.role_registry.list_roles():
            role = orchestrator.role_registry.get_role(role_name)
            role.human_callback = cli_interactive_callback

    result = orchestrator.execute_loop(loop_id)
```

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

## Questions to Answer

Before implementing, need to verify:

1. **Does RoleRegistry support human_callback parameter?**
   - Check `RoleRegistry.__init__()` and `.get_role()`
   - If yes, pass it when creating roles
   - If no, need alternative approach

2. **Does Orchestrator/Loop pass human_callback to roles?**
   - Check `Orchestrator.execute_loop()` flow
   - Check if LoopContext supports human_callback
   - Trace how roles are instantiated during loop execution

3. **Which roles actually use ask_human()?**
   - Check which role implementations call `self.ask_human()`
   - Showrunner? Lore Weaver? Scene Smith?
   - Know which loops benefit from interactive mode

4. **Are there examples/tests of interactive mode?**
   - Check `/tmp/questfoundry-py/tests/` for interactive tests
   - Look for examples in docs

---

## Action Items

### Immediate (Before Implementation)

- [ ] Read `RoleRegistry` implementation fully
- [ ] Trace `Orchestrator.execute_loop()` to see role creation
- [ ] Check tests for interactive mode examples
- [ ] Verify which roles use `ask_human()`

### Implementation

- [ ] Create `src/qf/interactive/callback.py`
- [ ] Add `--interactive` flag to `qf loop run`
- [ ] Wire up human_callback (method TBD based on research)
- [ ] Test with mock provider
- [ ] Document interactive mode in README

### Testing

- [ ] Unit test callback UI formatting
- [ ] Integration test with mock role asking questions
- [ ] End-to-end test: `qf loop run --interactive`

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

## Status

**Research needed:** Verify integration path (RoleRegistry vs LoopContext vs other)

**Implementation:** Deferred until research complete

**Priority:** Include in Phase 2 (loop execution) design
