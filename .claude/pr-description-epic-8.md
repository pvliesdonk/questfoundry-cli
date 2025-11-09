# Epic 8: Export & Views - Pull Request Description

## Summary

Epic 8 implements comprehensive export and view binding functionality for QuestFoundry CLI, enabling users to:

1. **Export snapshots as player-ready views** - Convert snapshots to HTML/Markdown formats
2. **Export snapshots as git-friendly YAML** - Create version-control-ready directory structures
3. **Bind and render views** - Use Book Binder role to generate final player-ready output

This epic completes the Layer 7 (CLI) implementation of view export and binding features, preparing for Layer 6 (Showrunner) integration.

## Features Implemented

### 1. Export Commands (`qf export`)

#### `qf export view`
- **Purpose**: Export snapshot as a player-ready view
- **Formats**: HTML (default), Markdown
- **Options**:
  - `--snapshot/-s`: Snapshot ID to export (optional, defaults to latest)
  - `--format/-f`: Output format (html/markdown)
  - `--output/-o`: Custom output file path
- **Example Usage**:
  ```bash
  qf export view                                    # Export latest to HTML
  qf export view --format markdown                  # Export as Markdown
  qf export view --snapshot snap-123 --output out.html  # Export specific snapshot
  ```

#### `qf export git`
- **Purpose**: Export snapshot in git-friendly format with YAML files
- **Output Structure**: Creates organized directory tree (metadata/, artifacts/, content/)
- **Options**:
  - `--snapshot/-s`: Snapshot ID to export (optional, defaults to latest)
  - `--output/-o`: Output directory path (default: snapshot_export/)
- **Example Usage**:
  ```bash
  qf export git                                 # Export to snapshot_export/
  qf export git --snapshot snap-123             # Export specific snapshot
  qf export git --output ./exports --snapshot snap-123  # Custom output
  ```

### 2. Bind Commands (`qf bind`)

#### `qf bind view`
- **Purpose**: Bind and render view from snapshot using Book Binder role
- **Formats**: HTML (default), Markdown, PDF
- **Options**:
  - Snapshot ID (required, positional argument)
  - `--format/-f`: Output format (html/markdown/pdf)
  - `--output/-o`: Custom output file path
- **Example Usage**:
  ```bash
  qf bind view snap-123                          # Render snapshot to HTML
  qf bind view snap-123 --format pdf              # Render as PDF
  qf bind view snap-123 --output bound.html       # Custom output path
  ```

## Implementation Details

### New Files Created

1. **`src/qf/commands/export.py`** (180 lines)
   - Implements export view and export git subcommands
   - Validates project existence and format options
   - Creates output files and directory structures
   - Provides Rich panel output for user feedback

2. **`src/qf/commands/bind.py`** (110 lines)
   - Implements bind view subcommand
   - Validates project existence and format options
   - Creates placeholder output files (ready for Layer 6 integration)
   - Displays binding progress and results

3. **`tests/commands/test_export.py`** (270+ lines)
   - 14 comprehensive test cases for export functionality
   - Tests for help text, project requirements, format validation
   - Tests for output paths, snapshot IDs, and progress display
   - Covers both export view and export git subcommands

4. **`tests/commands/test_bind.py`** (195+ lines)
   - 10 comprehensive test cases for bind functionality
   - Tests for help text, project requirements, snapshot IDs
   - Tests for format validation (HTML, Markdown, PDF)
   - Tests for output paths and default formats

### Modified Files

1. **`src/qf/cli.py`**
   - Added imports: `from .commands.bind import app as bind_app` and `from .commands.export import app as export_app`
   - Registered bind and export command groups via `app.add_typer()`
   - Integrated help text for both new command groups

## Test Coverage

- **Total tests**: 147 (up from 123 before Epic 8)
- **New tests**: 24 (14 for export, 10 for bind)
- **Test success rate**: 100% (147/147 passing)
- **Validation**: mypy type checking and ruff linting both pass

### Test Fixture Improvements

Fixed `mock_questionary_init` fixture to properly handle questionary's call chain:
- Captures original questionary.text function
- Creates wrapper that accepts message and kwargs
- Properly chains result.ask() method overrides
- Applied to both test_export.py and test_bind.py

## Design Decisions

1. **Placeholder Implementation**: Export/bind functions create placeholder files rather than full implementations, as Layer 6 (Showrunner) integration is pending. This allows:
   - Full CLI testing and validation
   - Future Layer 6 integration without CLI changes
   - Clear separation of concerns

2. **Format Validation**: Both commands validate format options early:
   - Export view: html, markdown
   - Bind view: html, markdown, pdf
   - Invalid formats are rejected with helpful error messages

3. **Directory Structure**: Git export creates organized structure:
   - `metadata/`: Snapshot metadata (snapshot.yml)
   - `artifacts/`: Artifact files (placeholder)
   - `content/`: Content files (placeholder)

4. **Rich Output**: All commands provide formatted output via Rich panels:
   - Success indicators (✓)
   - Execution information (format, snapshot, path)
   - Professional appearance consistent with other commands

## Integration Points

### Ready for Layer 6 Integration
- Export view/git and bind functions are well-structured placeholders
- Can accept integration from questfoundry-py Showrunner without CLI changes
- All validation and directory structure is in place

### Dependencies
- `typer`: CLI framework (already in use)
- `rich`: Formatted output (already in use)
- No new external dependencies added

## Commit Structure

Single commit with all Epic 8 implementation:
- feat(export-bind): add export view/git and bind view commands

Includes:
- New export and bind command implementations
- Comprehensive test suites (24 new tests)
- CLI registration and integration
- All type hints and documentation

## Validation Results

```
✓ All 147 tests pass (100%)
✓ mypy type checking: SUCCESS
✓ ruff linting: SUCCESS (23 issues fixed, 0 remaining)
```

## Next Steps

1. Layer 6 (Showrunner) integration to implement actual export/bind logic
2. Add support for additional export formats (JSON, YAML)
3. Streaming progress display for long-running exports
4. Integration with snapshot database for retrieving actual content

## Related Epics

- **Epic 5**: Loop execution and iteration tracking (merged)
- **Epic 6**: Asset generation (merged)
- **Epic 7**: Quickstart workflow (merged)
- **Epic 8**: Export & Views (this epic)

## Reviewer Checklist

- [ ] All tests pass (147/147)
- [ ] Type hints are complete (mypy validates)
- [ ] Code style matches project standards (ruff validates)
- [ ] Commands are properly registered in CLI
- [ ] Help text is clear and helpful
- [ ] Error handling provides good user feedback
- [ ] Placeholder structure supports Layer 6 integration
- [ ] Test coverage is comprehensive
