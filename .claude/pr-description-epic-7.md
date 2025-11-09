# Epic 7: Quickstart Workflow - Pull Request

## Summary

This PR implements Epic 7: Quickstart Workflow, adding a guided and interactive quickstart mode that helps users rapidly set up a QuestFoundry project and execute initial loops. The implementation includes comprehensive session management, checkpoint/resume functionality, and preparation for future Layer 6 Showrunner integration with dynamic loop sequencing.

## Features Implemented

### Core Functionality

✅ **Guided Quickstart Mode** (`qf quickstart`)
- Interactive project initialization with user prompts
- Setup questions: premise, tone, length, project name
- Project creation with workspace structure
- Sequential loop execution with progress feedback
- Checkpoint-based workflow with review and continue options
- Completion summary with next steps

✅ **Session Management** (`QuickstartSession` class)
- Project metadata tracking (name, premise, tone, length)
- Loop execution tracking (completed, current)
- Checkpoint save/load for resumable workflows
- Session state persistence
- Interactive mode flag management
- Status reporting with elapsed time

✅ **Interactive Prompts** (`interactive/prompts.py`)
- Questionary-based user input
- Premise text input with validation
- Tone/genre selection menu
- Length/scope selection menu
- Project name suggestion and input
- Setup confirmation dialog
- Loop continuation prompts
- Artifact review prompts

✅ **Resume Capability** (`--resume` flag)
- Checkpoint detection and loading
- Session state restoration
- Continuation from last executed loop
- Preservation of all project metadata

✅ **Interactive Mode** (`--interactive` flag)
- Foundation for agent collaboration
- Session state management for interactive execution
- Preparation for agent question handling
- Conversation context preservation

✅ **Quickstart Formatting** (`formatting/quickstart.py`)
- Project header display
- Completed loops visualization
- Showrunner decision display (placeholder)
- Loop goal/scope display helpers
- Progress tracking tables
- Artifact summary tables
- Completion messages
- Resume checkpoint messages

## Architecture & Design

### New Files Created

- **`src/qf/interactive/__init__.py`** (5 lines) - Module initialization
- **`src/qf/interactive/prompts.py`** (160 lines) - User prompt definitions using Questionary
- **`src/qf/interactive/session.py`** (210 lines) - QuickstartSession class with state management
- **`src/qf/commands/quickstart.py`** (230 lines) - Main quickstart command implementation
- **`src/qf/formatting/quickstart.py`** (180 lines) - Quickstart-specific display utilities
- **`tests/commands/test_quickstart.py`** (440 lines) - Comprehensive test suite

### Modified Files

- **`src/qf/cli.py`** - Imported and registered quickstart command

### Key Design Decisions

1. **Session Class**: Centralized state management for entire quickstart workflow
2. **Questionary Integration**: Consistent user prompts across entire workflow
3. **Checkpoint System**: Enables resumable workflows without database
4. **Modular Structure**: Separate concerns (prompts, session, formatting)
5. **Type Safety**: Full type hints on all functions
6. **Test-First Approach**: 20 tests covering all functionality
7. **Placeholder Architecture**: Ready for Layer 6 Showrunner integration

### Architectural Adaptations

The implementation follows the revised Layer 6 architecture (from LAYER_7_UPDATES_FOR_EPIC_7_8.md):

**Original Spec**: Hardcoded loop sequence (Hook Harvest → Lore Deepening → Story Spark)

**Current Implementation**:
- Foundation for Showrunner-driven loop sequencing
- Placeholder loop list (ready for dynamic replacement)
- Display functions for Showrunner reasoning
- Loop goal/scope display ready for actual loop metadata

**Future Integration Point**:
```python
# Will be replaced with:
next_loop = await showrunner.decide_next_loop(tu_context, completed_loops)
display_showrunner_suggestion(next_loop, reasoning)
```

## Test Coverage

**20 comprehensive tests** covering all scenarios:

### Session Management Tests (11 tests)
- ✅ Session initialization
- ✅ Project creation (with workspace structure)
- ✅ Loop start/complete tracking
- ✅ Loop completion idempotency
- ✅ Checkpoint save and load
- ✅ Resume capability detection
- ✅ Session status reporting
- ✅ Interactive mode enable/disable
- ✅ Checkpoint file persistence
- ✅ Invalid checkpoint handling
- ✅ Session metadata accuracy

### Command Tests (5 tests)
- ✅ Command invocation without project
- ✅ Help text display
- ✅ --guided flag recognition
- ✅ --interactive flag recognition
- ✅ --resume flag recognition

### Integration Tests (4 tests)
- ✅ Full project creation workflow
- ✅ Loop execution sequence
- ✅ Checkpoint save and resume workflow
- ✅ Interactive mode workflow

### Overall Results
- **109 total tests in suite**: All passing
- **20 new tests for quickstart**: All passing
- **Zero failures**: 100% pass rate

## Code Quality

### Linting & Type Checking
- ✅ **mypy**: No type errors (strict mode)
- ✅ **ruff**: All code quality checks passing
- ✅ **pytest**: 109/109 tests passing

### Code Statistics
```
src/qf/interactive/__init__.py        |   5 +
src/qf/interactive/prompts.py         | 160 ++++
src/qf/interactive/session.py         | 210 ++++++
src/qf/commands/quickstart.py         | 230 ++++++++
src/qf/formatting/quickstart.py       | 180 ++++++
src/qf/cli.py                         |   2 + (import + register)
tests/commands/test_quickstart.py     | 440 +++++++++++
7 files changed, 1227 insertions(+)
```

## Commits

This PR contains **1 major commit**:

1. `feat(epic-7): implement quickstart workflow with session management`
   - All interactive module files (prompts, session)
   - Main quickstart command
   - Formatting utilities
   - Comprehensive test suite
   - CLI integration

## Usage Examples

### Basic Quickstart (Guided Mode)
```bash
qf quickstart
# Answers prompts interactively
# Creates project
# Executes loops with checkpoints
```

### Interactive Mode
```bash
qf quickstart --interactive
# Same as above but with agent collaboration capability
```

### Resume Previous Session
```bash
qf quickstart --resume
# Loads checkpoint
# Continues from last loop
```

### Help
```bash
qf quickstart --help
# Shows all options and flags
```

## Detailed Workflow

### 1. Welcome & Setup
- Display welcome message
- Ask for story premise (validated)
- Ask for tone/genre
- Ask for story length
- Ask for project name (with suggestion)
- Confirm setup

### 2. Project Creation
- Create .questfoundry workspace
- Create subdirectories (hot, cold, assets)
- Write project.json with metadata
- Display confirmation

### 3. Loop Execution Loop
- Execute suggested loop (placeholder sequence)
- Show progress with spinner
- Mark loop as complete
- Save checkpoint
- Ask "Review artifacts?"
  - If yes: show artifact list (placeholder)
  - If no: continue
- Ask "Continue?"
  - If yes: continue to next loop
  - If no: pause and exit
- Repeat until all loops done

### 4. Completion
- Display final project summary
- Show list of completed loops
- Provide next steps guidance
- Suggest related commands

## Future Integration Points

### Layer 6 Showrunner Integration
```python
# In quickstart.py, replace placeholder with:
next_loop = showrunner.decide_next_loop(
    tu_context=session.get_session_status(),
    completed_loops=session.completed_loops
)
```

### Display Showrunner Reasoning
```python
from qf.formatting.quickstart import display_showrunner_suggestion

display_showrunner_suggestion(
    loop_name=next_loop,
    reasoning=showrunner.reasoning
)
```

### Dynamic Loop Metadata
```python
# Loop goals from Layer 6 loop registry
display_loop_goal(
    loop_name=next_loop,
    will_accomplish=loop_metadata['will_accomplish'],
    will_not=loop_metadata['will_not']
)
```

### Artifact Integration
```python
# Show actual artifacts created
artifact_count = workspace.count_artifacts()
display_artifact_summary(artifact_count, artifact_types)
```

## Definition of Done ✅

This epic meets the Definition of Done criteria:

- ✅ **All tests passing**: 109/109 tests pass
- ✅ **mypy passing**: No type errors in strict mode
- ✅ **ruff passing**: All code quality checks passing
- ✅ **Code formatted**: All code properly formatted
- ✅ **New tests added**: 20 comprehensive tests
- ✅ **Documentation**: Comprehensive docstrings
- ✅ **Error handling**: Graceful error handling throughout
- ✅ **CLI integration**: Command registered and working
- ✅ **Session management**: Complete state tracking
- ✅ **Checkpoint system**: Save/load/resume working

## Breaking Changes

None - this is a new feature addition with no impact on existing functionality.

## Dependencies

No new dependencies added. Uses existing:
- `typer` for CLI command implementation
- `questionary` for user prompts (already in dependencies)
- `rich` for formatting
- `pathlib` for file operations

## Documentation

All code includes:
- Comprehensive docstrings on all functions
- Clear help text for all CLI options
- Type hints on all parameters and returns
- Usage examples in code comments

## Testing Strategy

### Unit Tests
- Session class functionality
- Prompt definitions
- State management

### Integration Tests
- Full project creation workflow
- Loop execution sequence
- Checkpoint/resume workflow
- Interactive mode setup

### Manual Testing (Ready)
- Run `qf quickstart` interactively
- Test `--interactive` flag
- Test `--resume` functionality
- Test error handling (interrupted execution, invalid inputs)

## Known Limitations (Documented)

1. **Loop sequencing**: Currently uses placeholder loop list
   - Will be replaced with Showrunner-driven selection
   - Ready for Layer 6 integration

2. **Artifact display**: Currently shows placeholder message
   - Will show actual artifacts created by loops
   - Ready for Layer 6 integration

3. **Agent questions**: Interactive mode foundation only
   - Will be fully implemented with agent_questions.py
   - Session state management already in place

## Ready for Review

This PR is ready for final review and merge. All code meets quality standards, all 109 tests pass, and the implementation provides a solid foundation for guided project creation with ready-to-integrate placeholders for Layer 6 Showrunner functionality.

The implementation successfully adapts the original specification to the revised Layer 6 architecture while maintaining backward compatibility and providing a clean path for future enhancements.
