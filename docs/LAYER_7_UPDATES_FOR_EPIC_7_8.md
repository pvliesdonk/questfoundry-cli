# Layer 7 Updates for Epic 7/8 Revised Architecture

**Version:** 1.0 (2025-11-06)
**Related:** `06-libraries/EPIC_7_8_REVISED.md` v2.2
**Purpose:** Document how Layer 6 Epic 7/8 architecture changes affect Layer 7 CLI implementation

---

## Executive Summary

The revised Layer 6 architecture fundamentally changes how loops execute. Rather than linear single-pass progression, loops now "iterate until stable." This requires significant CLI updates across multiple epics.

**Core architectural shifts:**
- Loops converge through iteration, not linear execution
- A Showrunner (LLM-backed orchestrator) makes dynamic decisions
- Steps can trigger revisions of earlier work
- Each loop has fixed scope boundaries
- Showrunner maintains registry-level context but detailed context only for active loops

**Layer 7 impacts:**
- Epic 5 progress indicators must display iterations and stabilization
- Epic 7 quickstart cannot use hardcoded sequences
- Users need clear communication about revision cycles

---

## Layer 6 Architecture Changes

### Original Approach
Linear progression: Story Spark executes steps 1→2→3→...→8 in single pass, then completes.

### Revised Approach
Iterative stabilization:
- Iteration 1: Steps 1-7 execute; Gatekeeper blocks
- Iteration 2: Steps 1-3 revise based on issues; steps 4-7 re-execute; step 8 completes
- Loop stabilizes when quality criteria and validation pass

**Showrunner responsibilities:**
- Selects which agent role to activate for each step
- Approves or denies collaboration requests
- Decides which loop executes next from available registry
- Determines when loop has reached stability

**Loop scoping:**
- Story Spark: Plot development only (cannot alter style/art)
- Style Tune Up: Tone refinement only (cannot change plot/prose)
- Art Touch Up: Visual polish only (cannot change narrative)

---

## Epic-by-Epic Impact Analysis

### Epic 5: Loop Execution (`qf run <loop-name>`)

**Original assumption:** Single linear pass with sequential step completion.

**New reality:** Multi-iteration execution with possible revision cycles triggered by quality failures.

#### Required UX Changes

**5.1 Enhanced Progress Display**

Progress output must show:
- Iteration number clearly
- Which steps are revisions vs. first-pass
- Gatekeeper or other blocking points
- Showrunner's remediation decisions
- Final stabilization confirmation

**Example Output:**

```
Running Story Spark Loop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Iteration 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Step 1: Premise analysis (Lore Weaver)
✓ Step 2: Topology draft (Plotwright)
✓ Step 3: Hub design (Plotwright)
✓ Step 4: Gateway definition (Plotwright)
✓ Step 5: Beat sequencing (Plotwright)
✓ Step 6: Reachability check (Gatekeeper)
✓ Step 7: Preview generation (Scene Smith)
✗ Step 8: Quality gates (Gatekeeper)

Issues found:
  - Topology inconsistency: Hub-002 unreachable
  - Gateway validation: Missing condition for GATE-003

⟳ Showrunner: Revising topology (Steps 2-4)

Iteration 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
↻ Step 2: Topology revision (Plotwright)
↻ Step 3: Hub redesign (Plotwright)
↻ Step 4: Gateway refinement (Plotwright)
✓ Step 5: Beat sequencing (reused)
✓ Step 6: Reachability check (Gatekeeper)
✓ Step 7: Preview regeneration (Scene Smith)
✓ Step 8: Quality gates (Gatekeeper)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Loop Stabilized
Duration: 4m 12s (2 iterations)
Artifacts: 1 TU, 5 beats, 3 gateways created
```

**5.2 Progress API Modifications**

Replace simple linear progress with iteration-aware tracking:

```python
class LoopProgressTracker:
    def start_iteration(self, number: int):
        """Begin new iteration"""

    def start_step(self, name: str, agent: str, is_revision: bool = False):
        """Start step (first-pass or revision)"""

    def mark_blocked(self, step_name: str, issues: list[str]):
        """Mark step as blocked with issues"""

    def show_showrunner_decision(self, decision: str):
        """Display Showrunner's reasoning"""

    def complete_step(self, name: str):
        """Mark step complete"""

    def mark_stabilized(self):
        """Mark loop as stabilized"""
```

**5.3 Implementation Tasks**

Files requiring modification:
- `src/qf/commands/run.py` — iteration tracking
- `src/qf/formatting/progress.py` — iterative display support
- `src/qf/formatting/loop_summary.py` — iteration count and revision summaries

---

### Epic 7: Quickstart Workflow

**Original assumption:** Hardcoded sequence of loops executes in fixed order.

**New reality:** Showrunner determines which loop executes next based on project state and available artifacts.

#### Required UX Changes

**7.1 Dynamic Loop Sequencing**

Replace hardcoded loop lists with Showrunner-driven decisions:

```python
while loop_execution_continues:
    next_loop = await showrunner.decide_next_loop(
        tu_context,
        completed_loops
    )
    if next_loop is None:
        break
    result = await run_loop_with_progress(next_loop)
    show_checkpoint_prompt()
```

**Example Output:**

```
QuestFoundry Quickstart
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project initialized: coastal-mystery.qfproj

Completed Loops:
  ✓ Story Spark (4m 12s, 2 iterations)
  ✓ Lore Deepening (3m 45s, 1 iteration)

Showrunner suggests: Codex Expansion
Reason: Sufficient canon depth achieved; player-safe
        entries needed before scene writing begins

Continue with Codex Expansion? [Y/n]:
```

**7.2 Progress Tracking Update**

Completed loops display with iteration counts. "Pending" section removed (cannot be hardcoded). "Suggested next" from Showrunner shown instead with rationale.

**7.3 Loop Goal Communication**

Before each loop, display:
- Loop purpose statement
- What this loop WILL accomplish
- What this loop will NOT do (scope boundaries)

**Example:**

```
Starting: Codex Expansion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Create player-safe encyclopedia entries from canon

This loop WILL:
  ✓ Transform canonized hooks into codex entries
  ✓ Strip spoilers and internal reasoning
  ✓ Add accessibility metadata

This loop will NOT:
  ✗ Change plot or canon
  ✗ Write new scenes or prose
  ✗ Alter visual or audio assets

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**7.4 Implementation Updates**

Files requiring changes:
- `src/qf/commands/quickstart.py` — remove hardcoded sequence, integrate Showrunner calls
- `src/qf/formatting/quickstart.py` — display Showrunner reasoning and loop goals

New functions needed:
```python
def show_showrunner_decision(loop_name: str, reasoning: str):
    """Display Showrunner's loop selection reasoning"""

def show_loop_goal(loop_name: str, loop_metadata: dict):
    """Display loop purpose and scope boundaries"""
```

---

### Epic 6: Asset Generation (`qf generate`)

**Impact level:** Minimal

Asset generation itself remains unchanged, but artifact metadata should now include:
- Which loop created/revised the artifact
- Which iteration of that loop
- Stabilization state

---

### Epic 2: Artifact Inspection (`qf list`, `qf show`)

**Impact level:** Minor

Artifact displays should include:
- Loop name that created/revised artifact
- Iteration number where creation/revision occurred
- Duration of loop execution
- Stabilization status
- Full iteration history for traceability

**Example Output:**

```
Hook Card: HOOK-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Title:    The lighthouse keeper's final log entry
Status:   canonized
Stakes:   5 (out of 5)

Created:  2025-11-06 by Lore Weaver
Loop:     Story Spark (iteration 1)
Revised:  2025-11-06 by Lore Weaver (iteration 2)
Duration: 45s
State:    Stabilized
```

---

### Epic 4: Validation & Quality (`qf check`)

**Impact level:** Minimal

Gatecheck validation runs unchanged, but output should note:

```
Note: If gatecheck runs during a loop, Showrunner will
automatically revise earlier steps until issues are resolved.
```

---

## Optional New Features

### Loop Registry Explorer (`qf loops list/show`)

Discover available loops, their purposes, inputs/outputs, and scope boundaries.

```bash
$ qf loops list

Available Loops
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loop Name         Category      Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Story Spark       Discovery     Available
Hook Harvest      Discovery     Available
Lore Deepening    Discovery     Available
Codex Expansion   Discovery     Needs canon
Style Tune Up     Refinement    Needs prose
...

$ qf loops show story-spark

Loop: Story Spark
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Initial plot development and topology design

Scope:
  ✓ Creates plot topology (beats, hubs, loops, gateways)
  ✓ Generates hooks for future expansion
  ✗ Does NOT write full prose
  ✗ Does NOT create visual/audio assets
  ✗ Does NOT handle style/tone refinement

Inputs Required:
  - Project premise
  - Target length/complexity

Outputs Created:
  - TU brief
  - Topology structure
  - Hook cards
  - Preview prose snippets
```

Helps users understand when to run loops manually and why Showrunner makes certain sequence decisions.

### Showrunner Explain Mode (`qf run --explain`)

Display Showrunner's reasoning at each decision point:

```bash
$ qf run story-spark --explain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Showrunner: Activating Lore Weaver for Step 1

Decision reasoning:
  - Step requires premise analysis and world-building
  - Lore Weaver specializes in canon development
  - Alternative (Plotwright) better suited for Step 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Step 1: Premise analysis (Lore Weaver)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Showrunner: Activating Plotwright for Step 2

Decision reasoning:
  - Topology design is Plotwright's primary role
  - Premise context from Step 1 is sufficient
  - No collaboration needed at this stage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Valuable for transparency and debugging.

### Iteration Summary Display

After multi-iteration loops, show:

```
Loop Complete: Story Spark
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Iteration Summary:

Iteration 1 (2m 30s):
  - 7 steps completed
  - Blocked: Quality gate failed
  - Issues: Topology inconsistency, gateway validation

Iteration 2 (1m 42s):
  - 3 steps revised (Steps 2-4)
  - 4 steps reused (Steps 5-8)
  - Stabilized: All quality gates passed

Efficiency: 57% step reuse
Total duration: 4m 12s
```

---

## Implementation Roadmap

### Phase 1: Core Requirements (4-6 days additional)
- **Epic 5.1-5.3:** Multi-iteration progress tracking and display
- **Epic 7.1-7.2:** Dynamic quickstart sequencing with Showrunner integration

### Phase 2: Enhanced UX (2 days additional)
- Loop goal communication display
- Showrunner decision visibility in output

### Phase 3: Advanced Features (3-4 days, optional)
- Loop registry explorer
- Explain mode
- Iteration summaries

**Total additional effort:** 1-2 weeks beyond original estimate

---

## New and Modified Files

### New Files Required
```
src/qf/formatting/loop_progress.py
src/qf/formatting/showrunner.py
src/qf/formatting/iterations.py
src/qf/commands/loops.py
tests/formatting/test_loop_progress.py
tests/formatting/test_showrunner.py
tests/commands/test_loops.py
```

### Files Requiring Modification
```
src/qf/commands/run.py
src/qf/commands/quickstart.py
src/qf/commands/show.py
src/qf/formatting/progress.py
src/qf/formatting/loop_summary.py
src/qf/formatting/artifacts.py
tests/commands/test_run.py
tests/commands/test_quickstart.py
```

---

## Testing Strategy

New test scenarios needed:
- Single-iteration loops (no revisions)
- Two-iteration loops (one blocking event)
- Multi-iteration loops (multiple revision cycles)
- Showrunner following playbook recommendations
- Showrunner adapting recommendations based on context
- Collaboration approval/denial decisions
- Dynamic quickstart sequencing
- User checkpoint interruptions
- User overriding suggested sequences

Mock Showrunner must support scenario-based behavior for comprehensive testing.

---

## Documentation Updates

### User Guide Additions

**"Understanding Loop Iterations" section:**

Loops don't execute linearly but instead stabilize through iteration. When quality issues occur (such as Gatekeeper blocking), Showrunner determines which step to revise. Affected steps re-execute while unchanged steps are reused, ensuring both quality and efficiency.

**"How Showrunner Makes Decisions" section:**

Explains that Showrunner uses playbook recommendations as starting points but adapts based on project context. It maintains awareness of all available loops and suggests sequencing based on artifact readiness and project goals.

### Command Help Text Updates

`qf run --help` should clarify:

```
Loops execute steps until they stabilize. This may involve multiple
iterations if quality issues are found. The Showrunner orchestrates
execution and decides when the loop is complete.
```

---

## Key Takeaways

The Epic 7/8 revised architecture introduces iterative stabilization and intelligent orchestration, fundamentally changing CLI presentation requirements.

**Essential changes:**
- Progress displays must convey iteration and stabilization, not just linear advancement
- Quickstart requires dynamic sequencing rather than fixed loop order
- Users need transparent understanding of loop scope boundaries and Showrunner reasoning

**Benefits:**
- Revision cycles demonstrate quality assurance in action
- Showrunner reasoning removes black-box behavior
- Users can make informed manual loop decisions
- Scope boundaries prevent conflicting modifications across loops

**Timeline:** Core implementation adds approximately one week to development, with optional enhancements adding another week for comprehensive user experience improvements.

---

This document provides comprehensive guidance for updating Layer 7 CLI implementation to align with the revised Layer 6 architecture while maintaining strong user experience through transparent communication of loop execution, iteration, and orchestration decisions.
