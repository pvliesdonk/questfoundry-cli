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

**Create branch:**

```bash
git checkout -b claude/epic-<number>-<name>-<session-id>
```

Example:
```bash
git checkout -b claude/epic-1-project-foundation-011CUsGfkDUjdP1rxbTZSynV
```

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

**Code Quality:**
- ✅ All tests pass (`uv run pytest`)
- ✅ Type checking passes (`uv run mypy src/`)
- ✅ Linting passes (`uv run ruff check .`)
- ✅ Code formatted (`uv run ruff format .`)

**Review & Documentation:**
- ✅ At least one round of reviews completed
- ✅ All review feedback addressed
- ✅ Documentation updated (if applicable)

**Completeness:**
- ✅ All features implemented
- ✅ Commits follow conventional format
- ✅ No outstanding issues

**Branch Status:**
- ✅ All changes committed
- ✅ All changes pushed to remote branch
- ✅ Working tree clean

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

- `.claude/README.md` - Update current progress
- Todo list - Use TodoWrite tool for granular tracking
- Commit messages - Reference epic number

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
