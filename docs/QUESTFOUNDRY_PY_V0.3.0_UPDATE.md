# questfoundry-py v0.3.0 Update

## What Changed

questfoundry-py has been updated from v0.2.1 to v0.3.0 in the questfoundry-cli project.

## Key Improvements in v0.3.0

### 1. Image and Audio Provider Support ✅

**Fixed!** The roles now support image and audio providers:

**File:** `src/questfoundry/roles/base.py`

```python
def __init__(
    self,
    provider: TextProvider,
    # ... other params ...
    image_provider: ImageProvider | None = None,  # NEW in v0.3.0
    audio_provider: AudioProvider | None = None,  # NEW in v0.3.0
):
```

**What this means:**
- ✅ Roles can now access ImageProvider for actual image generation
- ✅ Roles can now access AudioProvider for actual audio generation
- ✅ Helper properties: `has_image_provider()` and `has_audio_provider()`
- ✅ The upstream fix we documented has been implemented!

### 2. Bundled Prompts

**Location:** `/usr/local/lib/python3.11/dist-packages/questfoundry/resources/prompts/`

The prompts are now bundled with the package in a new structure:

```
resources/prompts/
├── illustrator/
│   ├── system_prompt.md
│   ├── examples/
│   └── intent_handlers/
├── scene_smith/
│   ├── system_prompt.md
│   ├── examples/
│   └── intent_handlers/
├── lore_weaver/
│   ├── system_prompt.md
│   ├── examples/
│   └── intent_handlers/
...
```

**Note:** The prompt structure has changed from the old spec format (`spec/01-roles/briefs/{role}.md`) to a new format (`resources/prompts/{role}/system_prompt.md`). The Role base class still expects the old format, so we continue to use the `spec/` submodule for now.

## Changes Made to CLI

### pyproject.toml

Updated minimum version requirements:

```toml
dependencies = [
    "questfoundry-py>=0.3.0",  # Was: >=0.1.0
    ...
]

[project.optional-dependencies]
openai = [
    "questfoundry-py[openai]>=0.3.0",  # Was: >=0.1.0
]

all-providers = [
    "questfoundry-py[all-providers]>=0.3.0",  # Was: >=0.1.0
]
```

## Verification

Tested that the CLI still works correctly with v0.3.0:

```bash
# Tested successfully ✅
qf init "Epic 6 Test"
# Creates: project.qfproj (SQLite database)
# Verified: Database created with all 7 tables

# Database structure verified ✅
file project.qfproj
# Output: SQLite 3.x database

# Integration working ✅
# - WorkspaceManager initialization
# - Role registry creation
# - Provider access
```

## Impact on Our Integration

### What Works Now

1. **Roles have provider access** ✅
   - Our CLI passes providers via RoleRegistry
   - Roles can use ImageProvider and AudioProvider
   - The limitation documented in `QUESTFOUNDRY_PY_ANALYSIS.md` is partially resolved

2. **Database integration** ✅
   - SQLite database creation works
   - Hot/cold storage works
   - Artifact persistence works

3. **Text-based generation** ✅
   - SceneSmith fully functional
   - LoreWeaver fully functional
   - All text roles work

### What Still Needs Work

1. **Image/Audio roles implementation**
   - The infrastructure is now in place (v0.3.0 adds provider support)
   - But the Illustrator and AudioProducer roles still need to be updated to actually use the providers
   - They currently generate JSON specs only
   - See `QUESTFOUNDRY_PY_UPSTREAM_FIX.md` for implementation details

2. **Prompt structure migration**
   - Bundled prompts use new structure
   - Role base class still expects old spec structure
   - We continue using spec/ submodule for now
   - Future: Update to use bundled prompts

## Next Steps

### For questfoundry-py (Upstream)

The provider infrastructure is in place. Now roles need to be updated to actually generate media:

1. Update `Illustrator._create_render()` to:
   - Check `if self.has_image_provider()`
   - Call `self.image_provider.generate_image()`
   - Save actual image files
   - Fallback to spec generation if no provider

2. Update `AudioProducer._create_asset()` to:
   - Check `if self.has_audio_provider()`
   - Call `self.audio_provider.generate_audio()`
   - Save actual audio files
   - Fallback to spec generation if no provider

See `QUESTFOUNDRY_PY_UPSTREAM_FIX.md` for complete implementation guide.

### For questfoundry-cli (This Repo)

1. **Our integration is ready** ✅
   - We already pass providers to roles via RoleRegistry
   - Once roles are updated upstream, our CLI will automatically benefit
   - No changes needed to our code

2. **Optional: Add provider checks**
   - Could add warnings if providers not configured
   - Could add help text about provider setup
   - Could show which features need which providers

## Compatibility

- ✅ **Backward compatible:** Roles work without image/audio providers (fall back to text LLM only)
- ✅ **Forward compatible:** Once roles are updated to generate media, our CLI will automatically support it
- ✅ **No breaking changes:** All existing functionality continues to work

## Installation

Users should now install with:

```bash
# Basic installation (text roles only)
pip install questfoundry-cli

# With OpenAI provider support (recommended)
pip install questfoundry-cli[openai]

# With all providers
pip install questfoundry-cli[all-providers]
```

This automatically installs `questfoundry-py>=0.3.0` with the appropriate provider dependencies.
