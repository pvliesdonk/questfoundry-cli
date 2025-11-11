# Interactive Mode Integration - Orchestrator Enhancement Proposal

**For:** questfoundry-py maintainers
**From:** questfoundry-cli integration team
**Date:** 2025-11-11
**Issue:** Human callback (interactive mode) infrastructure exists but isn't wired through Orchestrator

---

## Summary

The human callback system for interactive mode is **fully implemented** in questfoundry-py v0.5.0 (roles/human_callback.py, roles/base.py), but the `Orchestrator.execute_loop()` method doesn't provide a way to pass callbacks to roles. This prevents downstream consumers (like questfoundry-cli) from implementing interactive mode where agents can ask users questions during loop execution.

**Proposed Solution:** Enhance `Orchestrator.execute_loop()` to extract `human_callback` from the config parameter and use `Showrunner.initialize_role_with_config()` to properly distribute it to roles.

---

## Current State

### ✅ What Works

**1. Human Callback Infrastructure (`roles/human_callback.py`)**
```python
HumanCallback = Callable[[str, dict[str, Any]], str]

def default_human_callback(question: str, context: dict[str, Any]) -> str:
    """Simple stdin prompt (reference implementation)"""
    # ...

def batch_mode_callback(question: str, context: dict[str, Any]) -> str:
    """Auto-responds for non-interactive mode"""
    # ...
```

**2. Role Support (`roles/base.py`)**
```python
class Role(ABC):
    def __init__(
        self,
        provider: TextProvider,
        human_callback: HumanCallback | None = None,  # ← Supported
        # ...
    ):
        self.human_callback = human_callback or batch_mode_callback

    def ask_human(
        self,
        question: str,
        suggestions: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Ask human a question (interactive mode)."""
        # Routes through callback
```

**3. Showrunner Coordination (`roles/showrunner.py:393-463`)**
```python
class Showrunner(Role):
    def initialize_role_with_config(
        self,
        role_class: type[Role],
        registry: ProviderRegistry,
        spec_path: Any | None = None,
        config: dict[str, Any] | None = None,
        session: Any | None = None,
        human_callback: Any | None = None,  # ← Accepts callback
        role_name: str | None = None,
    ) -> Role:
        """Initialize a role with provider configuration."""
        # Creates role WITH human_callback
        return role_class(
            provider=provider,
            spec_path=spec_path,
            config=config,
            session=session,
            human_callback=human_callback,  # ← Passes to role
            role_config=role_config,
        )
```

### ❌ What Doesn't Work

**Orchestrator doesn't wire it up (`orchestrator.py:185-273`)**

Current implementation:
```python
def execute_loop(
    self,
    loop_id: str,
    project_id: str,
    artifacts: list[Artifact] | None = None,
    config: dict[str, Any] | None = None,  # ← Config accepted but callback not extracted
) -> LoopResult:
    # ...

    # Instantiate required roles
    role_instances = {}
    required_roles = set(metadata.primary_roles + metadata.consulted_roles)

    for role_name in required_roles:
        try:
            # ❌ Uses RoleRegistry.get_role() which doesn't accept human_callback
            role_instances[role_name] = self.role_registry.get_role(
                role_name,
                provider=self.provider,
                provider_name=self.provider_name,
            )
        except KeyError:
            pass  # Role not implemented yet

    # ❌ Roles created WITHOUT human_callback support
    loop_context = LoopContext(
        loop_id=loop_id,
        project_id=project_id,
        workspace=self.workspace,
        role_instances=role_instances,  # ← No interactive capability
        artifacts=artifacts or [],
        project_metadata=project_info.model_dump(),
        config=config or {},
    )
```

---

## The Gap

1. `Orchestrator.execute_loop()` accepts `config` parameter
2. Config *could* contain `human_callback`
3. But Orchestrator doesn't extract it or pass it to roles
4. Roles are created via `RoleRegistry.get_role()` which doesn't accept callbacks
5. **Showrunner has the right method (`initialize_role_with_config`) but it's not being used**

---

## Proposed Solution

### Option 1: Use Showrunner for Role Initialization (RECOMMENDED)

This aligns with the spec's intent that **"Showrunner should be responsible for all human interaction"**.

```python
def execute_loop(
    self,
    loop_id: str,
    project_id: str,
    artifacts: list[Artifact] | None = None,
    config: dict[str, Any] | None = None,
) -> LoopResult:
    """
    Execute a specific loop.

    Args:
        loop_id: Loop identifier
        project_id: Project identifier
        artifacts: Existing artifacts
        config: Loop configuration, may include:
            - human_callback: Callback for agent-to-human questions (interactive mode)
            - Other loop-specific config

    Returns:
        Loop execution result
    """
    logger.info("Executing loop '%s' for project '%s'", loop_id, project_id)

    # Extract human_callback from config
    human_callback = (config or {}).get("human_callback")

    if human_callback:
        logger.debug("Interactive mode enabled - human_callback provided")

    # Get loop metadata
    metadata = self.loop_registry.get_loop_metadata(loop_id)

    # Instantiate required roles
    role_instances = {}
    required_roles = set(metadata.primary_roles + metadata.consulted_roles)
    logger.debug("Instantiating %d required roles", len(required_roles))

    # Get showrunner for coordinating role initialization
    if self.showrunner is None:
        raise RuntimeError("Orchestrator not initialized. Call initialize() first.")

    for role_name in required_roles:
        try:
            logger.trace("Getting role instance for '%s'", role_name)

            if role_name in self.role_registry._roles:
                role_class = self.role_registry._roles[role_name]

                # Use Showrunner to initialize roles with callback support
                role_instances[role_name] = self.showrunner.initialize_role_with_config(
                    role_class=role_class,
                    registry=self.provider_registry,
                    spec_path=self.spec_path,
                    human_callback=human_callback,  # ← Showrunner distributes callback
                    role_name=role_name,
                )
                logger.trace("Successfully instantiated role '%s'", role_name)
            else:
                logger.warning("Role '%s' not registered, skipping", role_name)

        except Exception as e:
            logger.warning("Failed to instantiate role '%s': %s", role_name, e)
            pass

    logger.debug("Successfully instantiated %d roles", len(role_instances))

    # Create loop context
    project_info = self.workspace.get_project_info()

    loop_context = LoopContext(
        loop_id=loop_id,
        project_id=project_id,
        workspace=self.workspace,
        role_instances=role_instances,  # ← Now with interactive capability
        artifacts=artifacts or [],
        project_metadata=project_info.model_dump(),
        config=config or {},
    )

    # Get loop class and instantiate
    loop_class = self._get_loop_class(loop_id)
    loop_instance = loop_class(loop_context)

    # Execute loop
    result = loop_instance.execute()

    if result.success:
        logger.info("Loop '%s' executed successfully", loop_id)
    else:
        logger.warning("Loop '%s' execution failed: %s", loop_id, result.error)

    return result
```

### Option 2: Extend RoleRegistry (ALTERNATIVE)

Add `human_callback` parameter to `RoleRegistry.get_role()`:

```python
# In roles/registry.py

def get_role(
    self,
    name: str,
    provider: TextProvider | None = None,
    provider_name: str | None = None,
    image_provider_name: str | None = None,
    audio_provider_name: str | None = None,
    human_callback: HumanCallback | None = None,  # ← Add this
) -> Role:
    """
    Get a role instance.

    Args:
        name: Role identifier
        provider: Text provider to use
        provider_name: Name of provider in registry
        image_provider_name: Optional image provider
        audio_provider_name: Optional audio provider
        human_callback: Optional callback for interactive mode
    """
    # ... existing provider setup ...

    # Create instance
    role_class = self._roles[name]
    config = self._configs.get(name, {})

    instance = role_class(
        provider=provider,
        spec_path=self.spec_path,
        config=config,
        image_provider=image_provider,
        audio_provider=audio_provider,
        human_callback=human_callback,  # ← Pass through
    )

    # Cache instance
    self._instances[name] = instance

    return instance
```

Then in `Orchestrator.execute_loop()`:

```python
# Extract callback
human_callback = (config or {}).get("human_callback")

for role_name in required_roles:
    try:
        role_instances[role_name] = self.role_registry.get_role(
            role_name,
            provider=self.provider,
            provider_name=self.provider_name,
            human_callback=human_callback,  # ← Pass to registry
        )
    except KeyError:
        pass
```

**Pros:** Simpler change, keeps existing flow
**Cons:** Doesn't align with spec's intent that Showrunner coordinates human interaction

---

## Recommendation

**Option 1** is preferred because:

1. **Aligns with spec:** "Showrunner should be responsible for all human interaction. It's the product manager so to speak"
2. **Uses existing infrastructure:** `Showrunner.initialize_role_with_config()` already exists for this purpose
3. **Better architecture:** Showrunner coordinates, not the registry
4. **Future-proof:** Showrunner can add coordination logic (logging, filtering, etc.)

---

## Downstream Use Case (questfoundry-cli)

With this enhancement, the CLI can provide a Rich UI callback:

```python
# In qf/commands/loop.py

from rich.console import Console
from rich.panel import Panel
import questionary

def cli_interactive_callback(question: str, context: dict[str, Any]) -> str:
    """CLI callback with Rich UI."""
    role = context.get("role", "Agent")
    suggestions = context.get("suggestions", [])

    # Display question in Rich panel
    console.print(
        Panel(
            f"[bold cyan]{question}[/bold cyan]",
            title=f"[{role}] Question",
            border_style="cyan",
        )
    )

    # Collect response with questionary
    if suggestions:
        return questionary.select(
            "Choose an option:",
            choices=[*suggestions, "Custom answer..."]
        ).ask()
    else:
        return questionary.text("Your answer:").ask()


def run(loop_id: str, interactive: bool = False):
    """Run a loop with optional interactive mode."""
    orchestrator = Orchestrator(workspace, provider_registry)
    orchestrator.initialize(provider_name="openai")

    # Prepare config
    loop_config = {}
    if interactive:
        loop_config["human_callback"] = cli_interactive_callback

    # Execute with callback support
    result = orchestrator.execute_loop(
        loop_id=loop_id,
        project_id=project_id,
        config=loop_config  # ← Callback passed through config
    )
```

**User Experience:**
```bash
$ qf loop run hook-harvest --interactive

Executing: Hook Harvest
⠋ Running loop...

┌─ [Lore Weaver] Question ────────────────────────┐
│ I'm analyzing your premise. Should the          │
│ supernatural elements be:                        │
│   a) Ambiguous (possibly natural explanations)  │
│   b) Clearly supernatural                        │
│   c) Something else?                             │
└──────────────────────────────────────────────────┘

? Choose an option:
  ❯ Ambiguous (possibly natural explanations)
    Clearly supernatural
    Custom answer...

✓ Hook Harvest complete!
Artifacts created: 5
```

---

## Backward Compatibility

✅ **Fully backward compatible:**

1. `config` parameter already exists in `execute_loop()`
2. If `config` doesn't contain `human_callback`, behavior is unchanged
3. If `human_callback` is not provided, roles default to `batch_mode_callback` (existing behavior)
4. No breaking changes to existing code

---

## Testing Considerations

**Unit Tests:**
```python
def test_execute_loop_with_human_callback():
    """Test that human_callback is properly distributed to roles."""
    callback_called = False

    def mock_callback(question: str, context: dict) -> str:
        nonlocal callback_called
        callback_called = True
        return "mock answer"

    orchestrator = Orchestrator(workspace, provider_registry)
    orchestrator.initialize(provider_name="mock")

    result = orchestrator.execute_loop(
        loop_id="test-loop",
        project_id="test-project",
        config={"human_callback": mock_callback}
    )

    # If any role called ask_human(), callback should have been invoked
    # (depends on loop implementation)
```

**Integration Tests:**
```python
def test_interactive_mode_end_to_end():
    """Test complete interactive workflow."""
    questions_asked = []

    def tracking_callback(question: str, context: dict) -> str:
        questions_asked.append({
            "question": question,
            "role": context.get("role"),
            "suggestions": context.get("suggestions", [])
        })
        # Auto-respond with first suggestion or empty
        return context.get("suggestions", [""])[0]

    # Execute loop with tracking callback
    result = orchestrator.execute_loop(
        loop_id="hook-harvest",
        project_id="test",
        config={"human_callback": tracking_callback}
    )

    # Verify interactions were tracked
    assert len(questions_asked) > 0
    assert all("role" in q for q in questions_asked)
```

---

## Implementation Checklist

- [ ] Choose Option 1 or Option 2
- [ ] Implement changes to `orchestrator.py`
- [ ] If Option 2: Add `human_callback` parameter to `RoleRegistry.get_role()`
- [ ] Add logging for interactive mode detection
- [ ] Add unit tests for callback distribution
- [ ] Add integration test for interactive workflow
- [ ] Update docstrings to document `config["human_callback"]`
- [ ] Update CHANGELOG.md
- [ ] Update documentation (if any exists for interactive mode)

---

## Questions for Maintainers

1. **Preference:** Option 1 (Showrunner-coordinated) or Option 2 (RoleRegistry passthrough)?
2. **Caching:** Should role instances be cached differently when `human_callback` is provided? (Currently RoleRegistry caches instances)
3. **Logging:** What log level for interactive mode events? (Currently using DEBUG/TRACE)
4. **Documentation:** Where should interactive mode integration be documented for library consumers?

---

## References

**Spec References:**
- `spec/05-prompts/_shared/human_interaction.md` - Human interaction pattern
- `spec/07-ui/README.md:198-254` - Interactive mode UX spec
- `spec/00-north-star/WORKING_MODEL.md:26` - "Showrunner — production lead; triggers loops; unblocks decisions"

**Code References:**
- `src/questfoundry/roles/human_callback.py` - Callback type and implementations
- `src/questfoundry/roles/base.py:166-200` - Role.ask_human() implementation
- `src/questfoundry/roles/showrunner.py:393-463` - Showrunner.initialize_role_with_config()
- `src/questfoundry/orchestrator.py:185-273` - Orchestrator.execute_loop() current implementation

---

## Contact

For questions or discussion about this proposal:
- **Repository:** questfoundry-cli integration team
- **Context:** Building CLI wrapper around questfoundry-py
- **Branch:** `claude/project-deep-dive-011CV2SD4HcVg8445vQ3uWjg`
