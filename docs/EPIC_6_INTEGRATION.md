# Epic 6 Integration: questfoundry-py Integration

## Status: Foundation Complete ✅

This document tracks the integration of questfoundry-py library into the CLI for Epic 6 (Asset Generation).

## Completed Work

### Phase 1: Foundation (Complete)

#### 1. Workspace Utility Module (`src/qf/utils/workspace.py`)
- ✅ `find_project_root()` - Locate `.questfoundry` directory
- ✅ `get_workspace()` - Create WorkspaceManager instances
- ✅ `require_workspace()` - CLI-friendly wrapper with error messages
- ✅ `is_questfoundry_project()` - Check if in QF project
- ✅ `get_spec_path()` - Locate questfoundry-spec directory
- ✅ Graceful handling of missing questfoundry-py dependency

#### 2. Providers Utility Module (`src/qf/utils/providers.py`)
- ✅ `get_provider_config()` - ProviderConfig creation
- ✅ `get_provider_registry()` - ProviderRegistry management
- ✅ `get_role_registry()` - RoleRegistry with spec path resolution
- ✅ `require_provider_registry()` - CLI-friendly provider access
- ✅ `require_role_registry()` - CLI-friendly role access
- ✅ Helpful error messages and installation hints

#### 3. Dependencies (`pyproject.toml`)
- ✅ Added `[openai]` extras for OpenAI provider support
- ✅ Added `[all-providers]` extras for all available providers
- ✅ Base questfoundry-py as core dependency

#### 4. Init Command Integration (`src/qf/commands/init.py`)
- ✅ Use `WorkspaceManager.init_workspace()` when available
- ✅ Creates proper SQLite database (`project.qfproj`)
- ✅ Initialize hot storage (`.questfoundry/hot/`) with correct structure
- ✅ Auto-detect author from git config or environment
- ✅ Fallback to legacy behavior if questfoundry-py not installed
- ✅ Updated success message to reflect SQLite database creation

#### 5. Verification Testing
- ✅ Tested `qf init` creates SQLite database (not JSON)
- ✅ Verified database contains all required tables:
  - schema_version, project, snapshots, views, artifacts, tus, history
- ✅ Verified project metadata is stored correctly in database
- ✅ Verified hot storage directory structure created properly

## Next Steps

### Phase 2: Generate Command Integration

#### Image Generation
- [ ] Update `generate.py` image command to use `Illustrator` role
- [ ] Replace `time.sleep()` simulation with real role execution
- [ ] Save generated artifacts to workspace
- [ ] Update progress display for real generation

#### Scene Generation
- [ ] Update `generate.py` scene command to use `SceneSmith` role
- [ ] Integrate with actual scene drafting
- [ ] Store scenes in workspace

#### Audio Generation
- [ ] Update `generate.py` audio command to use `AudioProducer` role
- [ ] Integrate with actual audio generation
- [ ] Store audio artifacts in workspace

#### Canonization
- [ ] Update `generate.py` canon command to use `LoreWeaver` role
- [ ] Integrate with actual canonization
- [ ] Store canon in workspace

#### Batch Generation
- [ ] Update batch generation to query workspace for pending artifacts
- [ ] Invoke appropriate roles for each artifact type

### Phase 3: Status Command Integration
- [ ] Update `status.py` to query workspace for active TUs
- [ ] Show pending artifacts from hot storage
- [ ] Show recent history from cold storage
- [ ] Remove placeholder messages

### Phase 4: Export/Bind Integration
- [ ] Update `export.py` to use ViewGenerator, BookBinder, GitExporter
- [ ] Update `bind.py` to use workspace artifact binding

### Phase 5: Cleanup
- [ ] Remove all 13+ placeholder messages
- [ ] Remove all `time.sleep()` simulation code
- [ ] Clean up imports and unused code

### Phase 6: Testing
- [ ] Add integration tests for workspace operations
- [ ] Add integration tests for role invocation
- [ ] Add integration tests for generate commands
- [ ] Update existing tests

### Phase 7: Documentation
- [ ] Update README with installation instructions
- [ ] Document provider configuration
- [ ] Document API key setup
- [ ] Update implementation plan

## Technical Notes

### SQLite Database Schema
The WorkspaceManager creates a complete SQLite database with:
- **project**: Singleton table with project metadata
- **artifacts**: Polymorphic artifact storage with JSON data
- **snapshots**: Immutable state captures
- **views**: Filtered perspectives on data
- **tus**: Thematic Unit state tracking
- **history**: Audit trail
- **schema_version**: Migration tracking

### Hot vs Cold Storage
- **Hot storage**: `.questfoundry/hot/` - File-based JSON for easy editing
- **Cold storage**: `project.qfproj` - SQLite database for stable content
- Promotion is explicit via CLI commands

### Spec Submodule
The `spec/` submodule (questfoundry-spec) provides role prompts.
Already initialized in the repository.

### Provider Configuration
Providers configured in `.questfoundry/config.yml` with environment variable substitution for API keys.

## Commits

1. `4eaa2bf` - feat(epic-6): add workspace utility module
2. `3abcbd7` - feat(epic-6): add providers utility module
3. `223e0e9` - feat(epic-6): add optional provider dependencies
4. `c37ac3c` - feat(epic-6): integrate WorkspaceManager into qf init

## Testing Commands

```bash
# Install with provider support
pip install -e ".[openai]"

# Test init
mkdir test-project && cd test-project
qf init

# Verify database created
file project.qfproj  # Should show "SQLite 3.x database"
ls .questfoundry/hot/  # Should show artifact directories

# Check database tables
python -c "import sqlite3; conn = sqlite3.connect('project.qfproj'); \
  cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); \
  print([row[0] for row in cursor.fetchall()])"
```

## Branch
`claude/plan-epic-6-integration-011CUzat9MEY6RnboSxm6r7m`
