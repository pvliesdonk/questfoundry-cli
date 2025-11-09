# Epic-Based Development Workflow

## Overview

Work is organized into **Epics** (large features) broken down into **Features** (individual commits).

```
Epic (Branch)
  ├── Feature 1 (Commit)
  ├── Feature 2 (Commit)
  └── Feature 3 (Commit)
```

## Workflow

### 1. Starting an Epic

**Every epic must have its own dedicated branch.**

**Create branch:**

```bash
git checkout -b claude/epic-<number>-<name>-<session-id>
```

Example:
```bash
git checkout -b claude/epic-1-project-foundation-011CUsGfkDUjdP1rxbTZSynV
```

**Note**: Do NOT reuse branches across epics. Each epic gets a new branch to maintain clean history and clear separation of concerns.

### 2. Implementing Features

For each feature in the epic:

#### A. Write Tests First (TDD)

```bash
# Create test file
touch tests/commands/test_init.py

# Write failing tests
# Run: uv run pytest tests/commands/test_init.py
```

#### B. Implement Feature

```bash
# Create/modify implementation files
# Run: uv run pytest tests/commands/test_init.py
```

#### C. Validate

```bash
uv run pytest          # All tests pass
uv run mypy src/       # Type checking passes
uv run ruff check .    # Linting passes
uv run ruff format .   # Code formatted
```

#### D. Commit

```bash
git add <files>
git commit -m "feat(commands): implement qf init command"
```

### 3. Quality Gates

Before committing, ensure:

- ✅ All tests pass
- ✅ Type checking passes
- ✅ Linting passes
- ✅ Code formatted

### 4. Push Epic

When all features complete:

```bash
# Verify everything
uv run pytest
uv run mypy src/
uv run ruff check .

# Push
git push -u origin claude/epic-<number>-<name>-<session-id>
```

### 5. Epic Completion - Definition of Done (DoD)

Before marking an epic as complete, it must meet the following criteria:

**CI/CD Green ✅**
- ✅ All tests pass: `uv run pytest` (no failures)
- ✅ Type checking passes: `uv run mypy src/` (no errors)
- ✅ Linting passes: `uv run ruff check .` (no violations)
- ✅ Code formatted: `uv run ruff format .`

**Review & Feedback:**
- ✅ At least one round of reviews completed (PR reviewed by maintainer or team)
- ✅ All review feedback addressed and resolved
- ✅ Any requested changes implemented
- ✅ Follow-up conversations documented

**Code Quality:**
- ✅ Documentation updated (if applicable)
- ✅ Test coverage adequate (>80% for new code)
- ✅ No technical debt introduced

**Completeness:**
- ✅ All features for the epic implemented
- ✅ Commits follow conventional format
- ✅ No outstanding issues or TODOs
- ✅ PR text written (see below)

**Branch Status:**
- ✅ All changes committed
- ✅ All changes pushed to remote branch
- ✅ Working tree clean
- ✅ Ready for merge to main

### Writing PR Text

**For each epic, create a PR text file** in `.claude/` directory:

```
.claude/pr-description-epic-<N>.md
```

**Template:**

```markdown
# Epic <N>: <Name> - Pull Request

## Summary
Brief overview of what was implemented.

## Features Implemented
- ✅ Feature 1
- ✅ Feature 2
- ✅ Feature 3

## Architecture & Design
Explain the design decisions and new/modified files.

## Test Coverage
List test scenarios covered.

## Code Quality
Report mypy, ruff, and pytest results.

## Commits
List all commits in the epic (can be copy-pasted from `git log`).

## Definition of Done ✅
- ✅ All tests passing
- ✅ mypy passing
- ✅ ruff passing
- ✅ At least one round of reviews completed and feedback addressed
```

**Benefits:**
- Clear communication of changes
- Easy to review before merging
- Historical record of what was done
- Helps track progress and completion

### 6. Cleanup

After epic merged:

```bash
git checkout main
git pull
git branch -d claude/epic-<number>-<name>-<session-id>
```

## Feature Commit Pattern

Each commit should be:

- ✅ **Self-contained**: Can be applied independently
- ✅ **Tested**: Includes tests for the feature
- ✅ **Typed**: Full type hints
- ✅ **Documented**: Includes docstrings
- ✅ **Conventional**: Follows commit format

### Commit Strategy

**Minimal Commits**: Preferably, one commit per feature. If a feature is complex and naturally decomposes, multiple commits are acceptable, but keep them minimal and logical.

**Why minimal?**
- Clean git history
- Easier to review
- Simpler to cherry-pick or revert if needed
- Better for understanding code evolution

**Examples:**

✅ **Good**: `feat(formatting): add multi-iteration loop tracking system`
- Creates 3 new modules + tests
- One logical feature
- One commit

❌ **Avoid**:
- Multiple commits for a single feature
- WIP or work-in-progress commits
- Commits that mix unrelated features

## Example Epic: Epic 1 - Project Foundation

```bash
# Create epic branch
git checkout -b claude/epic-1-project-foundation-<session-id>

# Feature 1.1: Repository setup
git commit -m "chore: initialize project structure"

# Feature 1.2: Package structure
git commit -m "feat: add main CLI entry point"

# Feature 1.3: Development tools
git commit -m "chore: configure ruff and mypy"

# Push epic
git push -u origin claude/epic-1-project-foundation-<session-id>
```

## Common Mistakes to Avoid

❌ **Oversized commits**: One commit doing multiple features
❌ **WIP commits**: Incomplete work pushed
❌ **Untested code**: Committing without running tests
❌ **Missing tests**: Features without test coverage
❌ **Unclear messages**: Vague commit descriptions

## Best Practices

✅ **Small commits**: One feature per commit
✅ **Test first**: Write tests before implementation
✅ **Validate always**: Run checks before committing
✅ **Clear messages**: Descriptive conventional commits
✅ **Document**: Update docs with features

## Epic Progress Tracking

Track epic progress in:

- `.claude/README.md` - Update current progress and mark epic as complete
- `.claude/pr-description-epic-<N>.md` - Write comprehensive PR text
- Todo list - Use TodoWrite tool for granular task tracking during development
- Commit messages - Reference epic number in conventional commits

## Example Epic Flow

```bash
# Start
git checkout -b claude/epic-2-core-commands-<session-id>

# Feature: qf init
uv run pytest tests/commands/test_init.py  # Write test (fails)
# Implement qf init
uv run pytest tests/commands/test_init.py  # Test passes
uv run mypy src/ && uv run ruff check .    # Validate
git commit -m "feat(commands): implement qf init command"

# Feature: qf list
uv run pytest tests/commands/test_list.py  # Write test (fails)
# Implement qf list
uv run pytest tests/commands/test_list.py  # Test passes
uv run mypy src/ && uv run ruff check .    # Validate
git commit -m "feat(commands): implement qf list command"

# Feature: qf show
uv run pytest tests/commands/test_show.py  # Write test (fails)
# Implement qf show
uv run pytest tests/commands/test_show.py  # Test passes
uv run mypy src/ && uv run ruff check .    # Validate
git commit -m "feat(commands): implement qf show command"

# Complete epic
uv run pytest                              # All tests pass
git push -u origin claude/epic-2-core-commands-<session-id>
```

## Summary

**Epic = Branch** containing multiple **Features = Commits**

Each commit is self-contained, tested, and follows conventional format. Epic completes when all features are implemented and validated.
