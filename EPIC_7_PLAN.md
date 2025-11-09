# Epic 7: Quickstart Workflow - Implementation Plan

## Overview

Epic 7 implements guided and interactive quickstart modes that help users quickly start a QuestFoundry project. The implementation is adapted for the revised Layer 6 architecture where the Showrunner dynamically determines loop sequences rather than following a hardcoded order.

## Key Architectural Changes vs. Original Spec

The original specification assumed a hardcoded loop sequence. However, the revised Layer 6 architecture (documented in `docs/LAYER_7_UPDATES_FOR_EPIC_7_8.md`) changes this fundamental approach:

### Original Approach
```
Hook Harvest → Lore Deepening → Story Spark → [additional loops in fixed order]
```

### New Approach (Showrunner-Driven)
```
Project Init → Ask Showrunner → [dynamic loop selection]
  ↓ (based on artifacts & state)
  → Show Showrunner's reasoning
  → Execute loop
  → Checkpoint
  → Repeat until complete
```

## Features to Implement

### 7.1: Quickstart Guided Mode

**Command**: `qf quickstart` (or `qf quickstart --guided`)

**Flow**:
1. **Welcome Message** - Greeting and quickstart overview
2. **Project Setup** - Interactive questions
   - Premise: Text input (story premise/concept)
   - Tone: Select from options (mystery, horror, adventure, sci-fi, etc.)
   - Length: Select (short story, novella, novel)
3. **Project Creation** - Create .qfproj and workspace
4. **Loop Execution Loop**:
   - Ask Showrunner for next recommended loop
   - Display Showrunner's reasoning
   - Display loop scope (WILL accomplish / will NOT do)
   - Execute loop with progress tracking
   - Show completion summary
   - **Checkpoint**: Ask "Review artifacts? [y/N]"
     - If yes: List artifacts, allow inspection
   - **Checkpoint**: Ask "Continue to [suggested loop]? [Y/n]"
     - If yes: Continue to next loop
     - If no: Pause and exit
5. **Completion Message** - Final summary and next steps

### 7.2: Quickstart Interactive Mode

**Command**: `qf quickstart --interactive`

**Differences from Guided**:
- Same setup and checkpoint flow
- During loop execution, agents can ask questions
- Display agent questions with context
- Accept free-form user responses
- Show conversation history
- Send responses back to agents
- Continue execution

**Agent Question Handling**:
```python
# During loop execution
question = agent.ask(context)
display_question(question)
response = prompt_user()
agent.respond(response)
```

### 7.3: Progress Tracking

**Display Elements**:
- Title: "QuestFoundry Quickstart"
- Project info (name, file)
- Completed Loops list with:
  - Loop name
  - Duration
  - Iteration count
  - Status (✓ Stabilized)
- **Showrunner Suggestion**:
  - Next loop name
  - Reasoning/explanation
- Option to continue

### 7.4: Loop Goal Display

**Before each loop, display**:
- Loop name and title
- Purpose statement
- **WILL accomplish** (✓ list of scope items)
- **will NOT do** (✗ list of out-of-scope items)

Example:
```
Starting: Codex Expansion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Create player-safe encyclopedia entries

This loop WILL:
  ✓ Transform canonized hooks into entries
  ✓ Strip spoilers and internal reasoning
  ✓ Add accessibility metadata

This loop will NOT:
  ✗ Change plot or canon
  ✗ Write new scenes or prose
  ✗ Alter visual or audio assets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Files to Create

```
src/qf/
  commands/
    quickstart.py              # Main quickstart command
  interactive/
    __init__.py
    prompts.py                 # User prompt/question definitions
    session.py                 # Quickstart session management
    agent_questions.py         # Agent question handling
  formatting/
    quickstart.py              # Quickstart-specific display formatting

tests/
  commands/
    test_quickstart.py         # Comprehensive tests
  interactive/
    test_prompts.py           # Prompts tests
    test_session.py           # Session tests
```

## Implementation Details

### 7.1: Guided Mode Implementation

```python
# src/qf/commands/quickstart.py

class QuickstartSession:
    def __init__(self):
        self.project_file = None
        self.completed_loops = []
        self.project_metadata = {}

    def welcome(self): → None
    def ask_setup_questions(self) → dict
    def create_project(self) → Project
    def run_quickstart(self) → None
    def ask_next_loop(self) → Optional[Loop]
    def checkpoint(self) → bool
    def cleanup(self) → None
```

### 7.2: Interactive Mode Implementation

```python
# src/qf/interactive/agent_questions.py

class AgentQuestionHandler:
    def display_question(self, question: dict) → None
    def prompt_response(self) → str
    def show_history(self) → None
    def handle_agent_interaction(self) → Response
```

### 7.3: Formatting Implementation

```python
# src/qf/formatting/quickstart.py

def display_quickstart_header() → None
def display_completed_loops(loops: list) → None
def display_showrunner_suggestion(loop: str, reason: str) → None
def display_loop_goal(loop_metadata: dict) → None
def display_completion_message() → None
def show_artifact_list() → None
```

### 7.4: Session Management

```python
# src/qf/interactive/session.py

class QuickstartSession:
    def save_checkpoint(self) → None
    def load_checkpoint(self) → None
    def can_resume(self) -> bool
    def get_session_status(self) -> dict
```

## Test Coverage Goals

**Guided Mode Tests** (~8 tests):
- ✅ Welcome message displays
- ✅ Setup questions flow
- ✅ Project creation
- ✅ Loop execution flow
- ✅ Checkpoints work
- ✅ Can review artifacts
- ✅ Can exit at checkpoint
- ✅ Showrunner integration

**Interactive Mode Tests** (~6 tests):
- ✅ Agent questions display
- ✅ Response handling
- ✅ Conversation history
- ✅ Multi-turn conversation
- ✅ Exit during interaction
- ✅ Context preservation

**Progress Tracking Tests** (~4 tests):
- ✅ Completed loops display
- ✅ Showrunner suggestion display
- ✅ Loop goal display
- ✅ Overall progress tracking

**Session Management Tests** (~4 tests):
- ✅ Session save/load
- ✅ Checkpoint functionality
- ✅ Session state tracking
- ✅ Resume capability

**Total Target**: ~22 comprehensive tests

## Dependencies

**Epic 6 (Asset Generation)**: ✅ Complete (required for artifact review)

**Layer 6 Integration Points**:
- Showrunner.decide_next_loop() - Dynamic loop selection
- Showrunner.run_loop() - Loop execution
- Showrunner.ask_question() - Agent questions (interactive mode)
- Project.create() - Project initialization
- Loop metadata - Scope information

## Implementation Order

1. **Phase 1**: Session management and setup flow
   - QuickstartSession class
   - Setup questions (premise, tone, length)
   - Project creation

2. **Phase 2**: Loop execution and progress tracking
   - Showrunner integration (decision + execution)
   - Progress display
   - Checkpoint flow

3. **Phase 3**: Interactive mode
   - Agent question handling
   - Response management
   - Conversation display

4. **Phase 4**: Formatting and polish
   - Loop goal display
   - Showrunner reasoning display
   - Completion message

5. **Phase 5**: Testing and documentation
   - Comprehensive test suite
   - PR documentation

## Key Design Decisions

1. **Async/Await**: Use async for Layer 6 Showrunner calls
2. **Session State**: Maintain in-memory + checkpoint for resume
3. **Questionary**: Use for interactive prompts (already in dependencies)
4. **Rich Formatting**: Consistent with previous epics
5. **Modular**: Separate concerns (prompts, session, formatting)

## Acceptance Criteria

- ✅ `qf quickstart` launches guided mode smoothly
- ✅ Setup questions flow naturally
- ✅ Showrunner integration works (dynamic loops)
- ✅ Checkpoints allow review and continuation
- ✅ Loop goals clearly communicated
- ✅ `qf quickstart --interactive` works with agent questions
- ✅ All tests pass (22+ tests)
- ✅ Type hints complete (mypy strict)
- ✅ Code formatted and linted

## Timeline Estimate

Based on Epic 6 effort (3-4 days):
- Phase 1-2: 2 days
- Phase 3-4: 2 days
- Phase 5: 1 day
- **Total**: 5 days

## Next Steps

1. Create quickstart.py with session management
2. Implement setup questions with Questionary
3. Integrate Showrunner loop decision calls
4. Build progress and formatting displays
5. Implement interactive mode
6. Write comprehensive tests
7. Document in PR description
