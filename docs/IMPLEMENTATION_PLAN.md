# Layer 7 Implementation Plan

**Target Agent:** GitHub Copilot or similar code-generation AI **Repository:**
`pvliesdonk/questfoundry-cli` **Language:** Python 3.11+ **Package Manager:** UV **CLI Framework:**
Typer (recommended) or Click

## Overview

Layer 7 provides the user-facing command-line interface. It wraps Layer 6 library functionality with
intuitive commands, rich formatting, and interactive features.

This is primarily about UX, formatting, and command routing - suitable for Copilot with clear
specifications.

---

## Epic 1: Project Foundation

**Goal:** Set up CLI repository structure and tooling.

**Dependencies:** None (can start immediately)

**Estimated Effort:** 1-2 days

### Features

#### 1.1: Repository Setup

**Files to create:**

```
questfoundry-cli/
  .gitignore
  .github/
    workflows/
      test.yml
      lint.yml
      release.yml        # PyPI release automation
  README.md
  LICENSE
  pyproject.toml
  uv.lock
```

**Tasks:**

- Initialize Python project with UV
- Configure `pyproject.toml`:
  - Package name: `questfoundry-cli`
  - Version: `0.1.0`
  - Python requirement: `>=3.11`
  - Dependencies:
    - `questfoundry>=0.1.0` (Layer 6 library)
    - `typer[all]>=0.9.0`
    - `rich>=13.0.0`
    - `questionary>=2.0.0` or `inquirerpy>=0.3.0`
    - `python-dotenv>=1.0.0`
  - Entry point: `qf = qf.cli:app`
- Set up GitHub Actions

**Acceptance Criteria:**

- `uv sync` works
- `qf --version` works after install
- CI/CD pipeline runs

---

#### 1.2: Package Structure

**Files to create:**

```
src/qf/
  __init__.py
  py.typed
  cli.py              # Main Typer app
  version.py
```

**Tasks:**

- Create src-layout package
- Set up Typer app
- Basic `--version` and `--help` commands

**Acceptance Criteria:**

- `qf --help` shows command list
- `qf --version` shows version

---

#### 1.3: Development Tools

**Files to create:**

```
.pre-commit-config.yaml
.ruff.toml
.mypy.ini
```

**Tasks:**

- Configure Ruff, mypy, pre-commit
- Add pytest configuration

**Acceptance Criteria:**

- Linting and type checking pass
- Test framework ready

---

## Epic 2: Core Commands (Phase 1)

**Goal:** Implement basic project and inspection commands.

**Dependencies:** Epic 1, Layer 6 Epic 1-3 (protocol, state)

**Estimated Effort:** 3-4 days

### Features

#### 2.1: Project Management Commands

**Files to create:**

```
src/qf/
  commands/
    __init__.py
    init.py
    open.py
    status.py
tests/
  commands/
    test_init.py
    test_status.py
```

**Commands to implement:**

**`qf init [path]`**

- Create new `.qfproj` file
- Initialize `.questfoundry/` workspace
- Prompt for project metadata (name, description)
- Create default config file
- Success message with next steps

**`qf open <project.qfproj>`**

- Validate project file exists
- Set as current project (store in config or env)
- Show project info

**`qf status`**

- Show current project
- List active roles
- Show pending artifacts
- Show recent TUs
- Use Rich tables for formatting

**Acceptance Criteria:**

- Can create new project
- Can open existing project
- Status shows meaningful info
- Good error messages

**Test Cases:**

- Init new project in empty directory
- Init in non-empty directory (error)
- Open non-existent project (error)
- Status with no active project (error)

---

#### 2.2: Artifact Listing Command

**Files to create:**

```
src/qf/
  commands/
    list.py
  formatting/
    __init__.py
    tables.py
tests/
  commands/
    test_list.py
```

**Command to implement:**

**`qf list <type>`**

- Types: `hooks`, `tus`, `canon`, `codex`, `shotlists`, `views`
- Query Layer 6 workspace
- Display as Rich table:
  - Columns: ID, Status, Title/Summary, Created
- Support filters: `--status proposed`, `--author LW`
- Pagination for large lists

**Acceptance Criteria:**

- Lists all artifact types
- Table formatting clear
- Filters work
- Empty list handled gracefully

**Test Cases:**

- List hooks in project with hooks
- List hooks in empty project
- Filter by status

---

#### 2.3: Artifact Inspection Command

**Files to create:**

```
src/qf/
  commands/
    show.py
  formatting/
    artifacts.py       # Artifact renderers
tests/
  commands/
    test_show.py
```

**Command to implement:**

**`qf show <artifact-id>`**

- Retrieve artifact from workspace
- Render as formatted display:
  - Use Rich panels/syntax highlighting
  - Show all fields
  - Highlight important info (status, author, TU)
  - Show related artifacts (links)
- Support JSON output: `--format json`

**Acceptance Criteria:**

- Shows artifact clearly
- Formatting is readable
- JSON output valid
- Non-existent artifact errors gracefully

**Test Cases:**

- Show hook card
- Show TU brief
- Show with `--format json`
- Show non-existent ID

---

#### 2.4: History Command

**Files to create:**

```
src/qf/
  commands/
    history.py
tests/
  commands/
    test_history.py
```

**Command to implement:**

**`qf history`**

- Show TU timeline
- Display as Rich tree or table
- Show: TU ID, loop, role, timestamp, summary
- Support filtering: `--loop "Hook Harvest"`, `--role LW`
- Link to artifacts created in each TU

**Acceptance Criteria:**

- Timeline is chronological
- Filters work
- Can see full TU details

---

## Epic 3: Configuration & Providers

**Goal:** Implement configuration management.

**Dependencies:** Epic 2, Layer 6 Epic 6 (providers)

**Estimated Effort:** 2-3 days

### Features

#### 3.1: Config Command

**Files to create:**

```
src/qf/
  commands/
    config.py
    provider.py
tests/
  commands/
    test_config.py
```

**Commands to implement:**

**`qf config list`**

- Show current configuration
- Format as tree or table
- Mask sensitive values (API keys)

**`qf config set <key> <value>`**

- Set configuration value
- Examples:
  - `qf config set provider.text.default openai`
  - `qf config set provider.text.openai.model gpt-4o`
- Validate before saving
- Confirm with success message

**`qf config get <key>`**

- Get specific config value
- Mask sensitive values

**`qf provider list`**

- List available providers
- Show: name, type (text/image), status (configured/not configured)
- Indicate current default

**Acceptance Criteria:**

- Can view config
- Can set config values
- Validation prevents invalid values
- Sensitive values masked

**Test Cases:**

- List empty config
- Set provider
- Get provider setting
- Set invalid value (error)

---

## Epic 4: Validation & Quality

**Goal:** Implement validation and gatecheck commands.

**Dependencies:** Epic 3, Layer 6 Epic 9 (quality bars)

**Estimated Effort:** 2-3 days

### Features

#### 4.1: Validation Command

**Files to create:**

```
src/qf/
  commands/
    validate.py
tests/
  commands/
    test_validate.py
```

**Commands to implement:**

**`qf validate <artifact-id>`**

- Validate single artifact against Layer 3 schema
- Show validation results:
  - ✓ Valid or ✗ Invalid
  - List all errors with field paths
  - Suggest fixes if possible
- Use Rich formatting for errors

**Acceptance Criteria:**

- Valid artifact shows success
- Invalid artifact shows clear errors
- Error messages actionable

**Test Cases:**

- Validate valid artifact
- Validate invalid artifact (missing field)
- Validate non-existent artifact

---

#### 4.2: Gatecheck Command

**Files to create:**

```
src/qf/
  commands/
    check.py
  formatting/
    quality.py         # Quality bar formatting
tests/
  commands/
    test_check.py
```

**Commands to implement:**

**`qf check`**

- Run all 8 quality bars via Layer 6
- Display results:
  - Table with bar name, status (✓/✗), violations count
  - Detailed violations if any
  - Summary: pass/fail
- Support: `--bars integrity,style` (specific bars only)
- Create gatecheck_report artifact

**Acceptance Criteria:**

- All bars run
- Results clearly displayed
- Failures show violations
- Report artifact created

**Test Cases:**

- Check passing project
- Check failing project (integrity violations)
- Check specific bars only

---

## Epic 5: Loop Execution

**Goal:** Implement manual loop execution commands.

**Dependencies:** Epic 4, Layer 6 Epic 7-8 (roles, orchestration)

**Estimated Effort:** 4-5 days

### Features

#### 5.1: Run Command

**Files to create:**

```
src/qf/
  commands/
    run.py
  formatting/
    progress.py        # Progress indicators
tests/
  commands/
    test_run.py
```

**Command to implement:**

**`qf run <loop-name>`**

- Execute specified loop via Layer 6 Showrunner
- Loops: `hook-harvest`, `lore-deepening`, `story-spark`, etc.
- Show progress:
  - Rich spinner or progress bar
  - Current activity (e.g., "Lore Weaver analyzing...")
  - Elapsed time
- Display summary at end:
  - TU created
  - Artifacts created/modified
  - Duration
- Support: `--interactive` flag (for Phase 3)

**Acceptance Criteria:**

- Can run all 11 loops
- Progress shown during execution
- Summary clear and informative
- Errors handled gracefully

**Test Cases:**

- Run hook-harvest successfully
- Run with no project open (error)
- Run invalid loop name (error)

---

#### 5.2: Loop Summary Formatting

**Files to create:**

```
src/qf/
  formatting/
    loop_summary.py
```

**Tasks:**

- Create rich summary display:
  - Loop name and duration
  - TU information
  - Artifacts created (table)
  - Next suggested action
- Use Rich panels, tables, and trees

**Acceptance Criteria:**

- Summary is visually appealing
- Information is complete
- Easy to scan

---

## Epic 6: Asset Generation

**Goal:** Implement individual asset generation commands.

**Dependencies:** Epic 5, Layer 6 Epic 6 (providers)

**Estimated Effort:** 3-4 days

### Features

#### 6.1: Generate Command

**Files to create:**

```
src/qf/
  commands/
    generate.py
tests/
  commands/
    test_generate.py
```

**Commands to implement:**

**`qf generate image <shotlist-id>`**

- Load shotlist artifact
- Execute Illustrator role via Layer 6
- Show progress (image generation can be slow)
- Display result:
  - Path to generated image
  - Option to open: `--open` flag
- Support: `--provider dalle`, `--model dall-e-3`

**`qf generate audio <cuelist-id>`**

- Load cuelist artifact
- Execute Audio Producer role via Layer 6
- Show progress
- Display result: path to audio file
- Support: `--provider elevenlabs`

**`qf generate scene <tu-id>`**

- Load TU brief
- Execute Scene Smith role via Layer 6
- Show generated prose
- Save as artifact

**`qf generate canon <hook-id>`**

- Load hook card
- Execute Lore Weaver role via Layer 6
- Show canonization result
- Save canon pack artifact

**Batch operations:** **`qf generate images --pending`**

- Generate all pending shotlists
- Progress bar for multiple generations

**Acceptance Criteria:**

- All generate types work
- Provider override works
- Progress shown
- Results saved correctly

**Test Cases:**

- Generate single image
- Generate with provider override
- Generate non-existent artifact (error)
- Batch generate

---

#### 6.2: Asset Preview

**Files to create:**

```
src/qf/
  formatting/
    assets.py
```

**Tasks:**

- Preview images in terminal (if supported)
- Use Rich image support or external viewer
- Format audio info (duration, format)

**Acceptance Criteria:**

- Images can be previewed or opened
- Audio info displayed

---

## Epic 7: Quickstart Workflow

**Goal:** Implement guided and interactive quickstart modes.

**Dependencies:** Epic 6, Layer 6 Epic 8 (orchestration complete)

**Estimated Effort:** 5-6 days

### Features

#### 7.1: Quickstart Guided Mode

**Files to create:**

```
src/qf/
  commands/
    quickstart.py
  interactive/
    __init__.py
    prompts.py         # User prompts/questions
    session.py         # Interactive session management
tests/
  commands/
    test_quickstart.py
```

**Command to implement:**

**`qf quickstart`** (guided mode default)

**Flow:**

1. Welcome message
2. Project initialization:
   - Ask setup questions (premise, tone, length)
   - Create project
3. Loop sequence:
   - Hook Harvest
   - Lore Deepening
   - Story Spark
   - (additional loops as needed)
4. After each loop:
   - Show summary
   - Ask: "Review artifacts? [y/N]"
   - If yes: show artifact list, allow inspection
   - Ask: "Continue to [next loop]? [Y/n]"
   - If no: pause and exit
5. Final completion message

**Prompts to use:**

- Use Questionary or InquirerPy for interactive prompts
- Text input for premise
- Select for tone (mystery, horror, adventure, etc.)
- Select for length (short, medium, long)

**Acceptance Criteria:**

- Smooth guided flow
- Clear checkpoints
- Can review before continuing
- Can exit at any checkpoint

**Test Cases:**

- Complete quickstart with Y/Y/Y
- Exit at first checkpoint
- Review artifacts between loops

---

#### 7.2: Quickstart Interactive Mode

**Files to create:**

```
src/qf/
  interactive/
    agent_questions.py
    renderer.py        # Rich rendering for conversations
```

**Command to implement:**

**`qf quickstart --interactive`**

**Differences from guided:**

- Agents can ask questions during loops
- Human responds free-form
- Conversational collaboration
- Questions displayed with context
- Responses sent back to agents

**Flow:**

1. Same setup questions
2. Enable interactive mode in Layer 6 Showrunner
3. When agent asks question:
   - Display question with context
   - Show suggestions if provided
   - Prompt for free-form answer
   - Send answer to agent
   - Agent continues
4. Same checkpoint flow

**Rendering:**

- Use Rich panels for questions
- Different colors for different roles
- Context shown clearly
- Response history visible

**Acceptance Criteria:**

- Agent questions displayed clearly
- Human can respond freely
- Conversation flows naturally
- History visible

**Test Cases:**

- Interactive mode with mocked agent questions
- Multi-turn conversation
- Exit during interaction

---

#### 7.3: Progress Tracking

**Files to create:**

```
src/qf/
  formatting/
    quickstart.py      # Quickstart-specific formatting
```

**Tasks:**

- Overall progress indicator:
  - Completed loops
  - Current loop
  - Pending loops
- Visual progress bar
- Time estimates (optional)

**Acceptance Criteria:**

- Clear progress indication
- User knows where they are in process

---

## Epic 8: Export & Views

**Goal:** Implement export and view generation commands.

**Dependencies:** Epic 7, Layer 6 Epic 10 (export)

**Estimated Effort:** 2-3 days

### Features

#### 8.1: Export Command

**Files to create:**

```
src/qf/
  commands/
    export.py
tests/
  commands/
    test_export.py
```

**Commands to implement:**

**`qf export view`**

- Generate player view from latest snapshot
- Options:
  - `--snapshot <id>`: Use specific snapshot
  - `--format html|markdown`: Output format
  - `--output <path>`: Output location
- Show progress
- Display result path

**`qf export git`**

- Export git-friendly snapshot (YAML files)
- Options:
  - `--snapshot <id>`: Use specific snapshot
  - `--output <path>`: Export directory
- Create directory structure
- Success message with path

**Acceptance Criteria:**

- View export works
- Multiple formats supported
- Git export creates valid YAML

**Test Cases:**

- Export view to HTML
- Export view to Markdown
- Export git-friendly snapshot

---

#### 8.2: Bind Command

**Files to create:**

```
src/qf/
  commands/
    bind.py
```

**Command to implement:**

**`qf bind view <snapshot-id>`**

- Execute Book Binder role
- Generate view from snapshot
- Options:
  - `--format html|markdown|pdf`: Target format
  - `--output <path>`: Output path
- Show progress
- Display result

**Acceptance Criteria:**

- Book Binder executed correctly
- View generated
- Multiple formats supported

---

## Epic 9: Shell Completion

**Goal:** Implement shell autocomplete support.

**Dependencies:** Epic 8

**Estimated Effort:** 2-3 days

### Features

#### 9.1: Completion Scripts

**Files to create:**

```
src/qf/
  completions/
    __init__.py
    bash.py
    zsh.py
    fish.py
```

**Tasks:**

- Generate completion scripts for each shell
- Dynamic completions:
  - Artifact IDs (from current project)
  - Loop names (from Layer 0)
  - Provider names (from Layer 6)
  - Config keys (from schema)
- Use Typer's built-in completion support

**Commands to implement:**

**`qf --install-completion [bash|zsh|fish]`**

- Generate and install completion script
- Add to appropriate rc file
- Show instructions for manual installation

**`qf --show-completion [bash|zsh|fish]`**

- Display completion script
- For manual installation

**Acceptance Criteria:**

- Completion works in all three shells
- Dynamic completions accurate
- Easy installation

**Test Cases:**

- Install completion for bash
- Test artifact ID completion
- Test loop name completion

---

#### 9.2: Dynamic Completion Functions

**Files to create:**

```
src/qf/
  completions/
    dynamic.py
```

**Tasks:**

- Implement completion functions:
  - `complete_artifact_id()`: List all artifact IDs in project
  - `complete_loop_name()`: List all loop names
  - `complete_provider_name()`: List available providers
- Handle no-project case gracefully

**Acceptance Criteria:**

- Completions load quickly (<200ms)
- No errors when no project open
- Results are relevant

---

## Epic 10: Advanced Features (Phase 5)

**Goal:** Implement advanced CLI features.

**Dependencies:** Epic 9

**Estimated Effort:** 3-4 days

### Features

#### 10.1: Diff Command

**Files to create:**

```
src/qf/
  commands/
    diff.py
```

**Command to implement:**

**`qf diff <artifact-id>`**

- Show changes across versions
- Use Rich diff rendering
- Compare:
  - Current hot vs last cold
  - Between two TUs
  - Between snapshots

**Acceptance Criteria:**

- Clear diff display
- Color-coded changes

---

#### 10.2: Search Command

**Files to create:**

```
src/qf/
  commands/
    search.py
```

**Command to implement:**

**`qf search <query>`**

- Full-text search across artifacts
- Options:
  - `--type hooks`: Search specific type
  - `--field title`: Search specific field
- Display results as table with matches highlighted

**Acceptance Criteria:**

- Fast search
- Relevant results
- Match highlighting

---

#### 10.3: Interactive Shell (REPL)

**Files to create:**

```
src/qf/
  commands/
    shell.py
```

**Command to implement:**

**`qf shell`**

- Drop into interactive REPL
- All commands available without `qf` prefix
- Context maintained between commands
- Use prompt_toolkit or similar

**Acceptance Criteria:**

- REPL works
- Command history
- Tab completion

---

## Epic 11: Documentation & Polish

**Goal:** Complete documentation and user guides.

**Dependencies:** Epic 10

**Estimated Effort:** 2-3 days

### Features

#### 11.1: User Documentation

**Files to create:**

```
docs/
  index.md
  installation.md
  quickstart_tutorial.md
  commands/
    init.md
    run.md
    generate.md
    [... all commands]
  guides/
    first_project.md
    working_with_loops.md
    generating_assets.md
```

**Tasks:**

- Comprehensive command reference
- Step-by-step tutorials
- Screenshots/GIFs of CLI in action
- Troubleshooting guide

**Acceptance Criteria:**

- All commands documented
- Tutorials tested and work
- Clear and beginner-friendly

---

#### 11.2: Help Text Polish

**Tasks:**

- Review all command help text
- Ensure consistency
- Add examples to help text
- Group related commands

**Acceptance Criteria:**

- `qf --help` is clear and organized
- Each command has good help text with examples

---

#### 11.3: Error Message Improvement

**Files to create:**

```
src/qf/
  errors.py          # Custom error messages
```

**Tasks:**

- Standardize error messages
- Make errors actionable
- Suggest fixes where possible
- Use Rich formatting for errors

**Acceptance Criteria:**

- Errors are friendly
- Suggest solutions
- No cryptic messages

---

## Epic 12: Package Distribution

**Goal:** Prepare for PyPI distribution.

**Dependencies:** Epic 11

**Estimated Effort:** 1-2 days

### Features

#### 12.1: Package Metadata

**Tasks:**

- Polish README with badges
- Create CHANGELOG.md
- Add LICENSE
- Configure classifiers in pyproject.toml
- Add keywords for PyPI search

**Acceptance Criteria:**

- Professional README
- Clear versioning
- Proper licensing

---

#### 12.2: Release Automation

**Files to create:**

```
.github/
  workflows/
    release.yml       # Automated PyPI release
```

**Tasks:**

- Set up GitHub Actions for release
- Build wheels for multiple platforms
- Publish to PyPI on tag
- Create GitHub releases

**Acceptance Criteria:**

- Tagging triggers release
- Wheels built correctly
- PyPI upload works

---

#### 12.3: Installation Testing

**Tasks:**

- Test installation in clean environments
- Test on Windows, macOS, Linux
- Test with different Python versions (3.11, 3.12, 3.13)
- Verify all dependencies install correctly

**Acceptance Criteria:**

- Installs cleanly everywhere
- No missing dependencies
- Entry point works

---

## Testing Strategy

### Unit Tests

- Each command has test file
- Mock Layer 6 calls
- Test command output formatting
- Test error cases

### Integration Tests

**Files to create:**

```
tests/
  integration/
    test_full_workflow.py
    test_quickstart.py
    test_generate_assets.py
```

**Tasks:**

- Test complete workflows
- Use real Layer 6 (with mocked LLMs)
- Test checkpoint flows
- Test error recovery

### Manual Testing

**Checklist:**

- [ ] Install from source
- [ ] Run quickstart end-to-end
- [ ] Generate image
- [ ] Export view
- [ ] Test in all three shells
- [ ] Test on Windows, macOS, Linux

---

## Implementation Order Summary

**Phase 1: Foundation**

1. Epic 1: Project Foundation

**Phase 2: Basic Operations** 2. Epic 2: Core Commands (init, list, show, status, history) 3. Epic
3: Configuration & Providers

**Phase 3: Validation & Execution** 4. Epic 4: Validation & Quality (validate, check) 5. Epic 5:
Loop Execution (run)

**Phase 4: Asset Generation** 6. Epic 6: Asset Generation (generate)

**Phase 5: Quickstart** 7. Epic 7: Quickstart Workflow (guided and interactive)

**Phase 6: Export** 8. Epic 8: Export & Views (export, bind)

**Phase 7: Polish** 9. Epic 9: Shell Completion 10. Epic 10: Advanced Features (diff, search,
shell) 11. Epic 11: Documentation & Polish 12. Epic 12: Package Distribution

---

## AI Agent Instructions (for Copilot)

### Context to Provide

When working with Copilot on Layer 7:

**Essential Context:**

```
You are creating a CLI tool for the QuestFoundry system.

Background:
- QuestFoundry is a system for creating interactive narratives
- Layer 6 (questfoundry library) provides all business logic
- Layer 7 (THIS LAYER) provides CLI UX wrapper

Your task: Create intuitive, beautiful CLI commands.

Key principles:
- Use Typer for command framework
- Use Rich for beautiful output
- Wrap Layer 6 library calls
- Handle errors gracefully
- Provide clear feedback
- Make it feel polished

Tech stack:
- Typer: CLI framework
- Rich: Terminal formatting
- Questionary: Interactive prompts
- Python 3.11+
```

### Code Patterns to Follow

**Command structure:**

```python
import typer
from rich.console import Console
from questfoundry import ProtocolClient, Workspace

app = typer.Typer()
console = Console()

@app.command()
def list(
    type: str = typer.Argument(..., help="Artifact type to list"),
    status: Optional[str] = typer.Option(None, help="Filter by status")
):
    """List artifacts in the project."""
    try:
        # Load workspace
        workspace = Workspace.load_current()

        # Query artifacts
        artifacts = workspace.list_artifacts(type=type, status=status)

        # Format as table
        table = create_artifact_table(artifacts)
        console.print(table)

    except WorkspaceNotFoundError:
        console.print("[red]No project open. Use 'qf init' or 'qf open'[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
```

**Rich formatting:**

```python
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

def create_artifact_table(artifacts):
    table = Table(title="Hooks")
    table.add_column("ID", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Title", style="green")

    for artifact in artifacts:
        table.add_row(artifact.id, artifact.status, artifact.title)

    return table
```

**Progress indicators:**

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console,
) as progress:
    task = progress.add_task("Running Hook Harvest...", total=None)
    result = showrunner.run_loop("hook-harvest")
    progress.update(task, completed=True)
```

**Interactive prompts:**

```python
import questionary

premise = questionary.text(
    "What's your story premise?",
    validate=lambda x: len(x) > 10 or "Please provide more detail"
).ask()

tone = questionary.select(
    "What tone?",
    choices=["Mystery", "Horror", "Adventure", "Sci-Fi"]
).ask()
```

### Quality Checklist

For each command:

- [ ] Help text is clear and has examples
- [ ] All options have descriptions
- [ ] Errors show helpful messages
- [ ] Success is confirmed clearly
- [ ] Rich formatting used appropriately
- [ ] No bare print() statements (use console)
- [ ] Tests written
- [ ] Type hints complete

### Testing Patterns

```python
from typer.testing import CliRunner
from qf.cli import app

runner = CliRunner()

def test_list_hooks():
    result = runner.invoke(app, ["list", "hooks"])
    assert result.exit_code == 0
    assert "HOOK-" in result.stdout

def test_list_no_project():
    result = runner.invoke(app, ["list", "hooks"])
    assert result.exit_code == 1
    assert "No project open" in result.stdout
```

---

## Success Criteria

Layer 7 is complete when:

- [ ] All 12 epics implemented
- [ ] All commands work end-to-end
- [ ] Quickstart works (guided and interactive)
- [ ] Asset generation works
- [ ] Shell completion works
- [ ] Test coverage >70%
- [ ] Documentation complete
- [ ] Installable via `pip install questfoundry-cli`
- [ ] Works on Windows, macOS, Linux
- [ ] User testing feedback positive

---

## Estimated Timeline

**Aggressive (Full-time AI agent):** 6-8 weeks **Moderate (Part-time):** 10-12 weeks
**Conservative:** 16-20 weeks

Assumes Copilot with human review at epic boundaries.

---

## Dependencies

**Layer 6 Dependencies:**

- Epic 2 depends on Layer 6 Epic 1-3 (protocol, state)
- Epic 4 depends on Layer 6 Epic 9 (quality bars)
- Epic 5 depends on Layer 6 Epic 7-8 (roles, orchestration)
- Epic 6 depends on Layer 6 Epic 6 (providers)
- Epic 7 depends on Layer 6 Epic 8 (orchestration complete)
- Epic 8 depends on Layer 6 Epic 10 (export)

**Can start immediately:** Epic 1 (foundation)

**Parallel work possible:** Epics 2-3 can be developed while Layer 6 progresses, using mocked Layer
6 responses.

---

## Notes for Human Reviewers

**What to look for:**

- Is the UX intuitive?
- Are error messages helpful?
- Is the formatting clear and readable?
- Are commands discoverable?
- Is the help text useful?
- Does it feel polished?

**Common issues to watch for:**

- Unclear command names
- Missing error handling
- Bare print statements (should use Rich)
- No progress feedback for long operations
- Inconsistent formatting
- Missing examples in help text

**Best CLIs have:**

- Intuitive command structure
- Beautiful, color-coded output
- Clear progress indicators
- Helpful error messages
- Good documentation
- Fast autocomplete
- Consistent experience
