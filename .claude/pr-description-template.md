# Epic <N>: <Epic Name> - Pull Request Template

**Use this template when creating PR text for each epic.** Save as `.claude/pr-description-epic-<N>.md`

## Summary

Brief 2-3 sentence overview of what this epic implements and why it's valuable.

## Features Implemented

List all major features/capabilities added:

- ✅ Feature 1: Brief description
- ✅ Feature 2: Brief description
- ✅ Feature 3: Brief description

## Architecture & Design

### New Files Created

Document any new files:

```
src/qf/module/
├── feature1.py       # Description (X lines)
├── feature2.py       # Description (X lines)
└── __init__.py
tests/
├── test_feature1.py  # Description (X tests)
└── test_feature2.py  # Description (X tests)
```

### Modified Files

Document files that were changed:

```
src/qf/cli.py        # Added registration of new commands
src/qf/utils.py      # Updated helper functions
```

### Design Decisions

Explain why you chose this approach:

- **Decision 1**: Why this choice over alternatives
- **Decision 2**: Why this choice over alternatives

## Test Coverage

Document test scenarios and coverage:

```
test_feature1.py
├── test_feature1_basic       # Basic functionality
├── test_feature1_edge_cases  # Edge cases
└── test_feature1_errors      # Error handling

test_feature2.py
├── test_feature2_basic       # Basic functionality
└── test_feature2_integration # Integration tests

Total: XX tests across Y test files
Test Results: ✅ All tests passing
```

## Code Quality

Report the state of code quality checks:

```bash
# All must pass for epic to be marked done
uv run pytest          # ✅ XX/XX tests passing
uv run mypy src/       # ✅ No type errors
uv run ruff check .    # ✅ No linting issues
uv run ruff format .   # ✅ Code formatted
```

## Commits

List all commits in this epic (can be copy-pasted from `git log`):

```bash
abc1234 feat(scope): implement feature 1
def5678 feat(scope): implement feature 2
ghi9012 test(scope): add comprehensive tests
jkl3456 fix(scope): address code quality issues
mno7890 docs: update documentation
```

## Usage Examples

Show how to use the new features:

```bash
# Example 1
command --option value

# Example 2
command --flag
```

## Breaking Changes

State if any breaking changes were introduced:

- None (or describe what changed)

## Dependencies

List any new or updated dependencies:

- New package X @ version Y
- Updated package Z from v1.0 to v2.0

## Definition of Done ✅

Epic completion checklist:

- ✅ All tests passing: `uv run pytest`
- ✅ mypy passing: `uv run mypy src/`
- ✅ ruff passing: `uv run ruff check .`
- ✅ At least one round of reviews completed
- ✅ All review feedback addressed
- ✅ Branch pushed to remote: `git push -u origin <branch>`
- ✅ PR text written and saved

## Future Work

(Optional) Note anything that might be addressed in future epics:

- Future improvement 1
- Future improvement 2

---

**Note**: This PR text becomes part of the permanent record. It should be comprehensive enough that someone reading it 6 months from now understands what was built, why, and how.
