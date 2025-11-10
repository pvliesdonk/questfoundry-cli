# questfoundry-py Integration Analysis

## Executive Summary

**Critical Finding:** The questfoundry-py roles for image and audio generation are **NOT actually generating media files**. They only generate JSON specifications describing what *should* be generated.

## What's Actually Implemented

### ✅ Fully Functional Roles (Text-based)

These roles work properly with text LLM providers:

1. **SceneSmith** - Generates actual narrative prose ✅
2. **LoreWeaver** - Generates canonical lore text ✅
3. **Plotwright** - Generates story structure ✅
4. **Gatekeeper** - Performs validation ✅
5. **CodexCurator** - Generates encyclopedia entries ✅
6. **StyleLead** - Style guidance ✅
7. **Translator** - Translation ✅
8. **BookBinder** - Formatting ✅
9. **Showrunner** - Orchestration ✅

### ⚠️ Partially Implemented Roles (Specification Only)

These roles generate **specifications**, not actual media:

1. **Illustrator** - Returns JSON render spec, not images ⚠️
2. **AudioProducer** - Returns JSON audio spec, not audio files ⚠️
3. **ArtDirector** - Returns art plans (specs for Illustrator) ⚠️
4. **AudioDirector** - Returns audio plans (specs for AudioProducer) ⚠️

## Technical Details

### Role Architecture Limitation

**File:** `/tmp/questfoundry-py/src/questfoundry/roles/base.py` (line 87)

```python
def __init__(
    self,
    provider: TextProvider,  # <-- Only TextProvider, no ImageProvider!
    spec_path: Path | None = None,
    config: dict[str, Any] | None = None,
    ...
):
```

**Key Issue:** All roles only receive a `TextProvider`. They cannot access `ImageProvider` or `AudioProvider`.

### Illustrator Implementation

**File:** `/tmp/questfoundry-py/src/questfoundry/roles/illustrator.py` (lines 89-91)

```python
Note: In a real implementation, this would interface with image generation.
For now, provide a detailed rendering specification.
```

**What it actually does:**
- Takes an art plan as input
- Calls a text LLM to generate a JSON specification
- Returns metadata like:
  ```json
  {
    "render_spec": {
      "composition": "Detailed composition description",
      "technical_params": {
        "seed": "...",
        "aspect_ratio": "...",
        "palette": ["color1", "color2"]
      }
    },
    "alt_text": "Accessibility description"
  }
  ```

**What it does NOT do:**
- ❌ Call DALL-E, Stable Diffusion, or any image generation API
- ❌ Generate actual image files
- ❌ Save PNG/JPG files to disk

### AudioProducer Implementation

**File:** `/tmp/questfoundry-py/src/questfoundry/roles/audio_producer.py` (lines 90-91)

```python
Note: In a real implementation, this would interface with audio generation/DAW.
For now, provide a detailed production specification.
```

**What it actually does:**
- Takes an audio plan as input
- Calls a text LLM to generate a JSON specification
- Returns metadata like:
  ```json
  {
    "asset_spec": {
      "description": "Production approach",
      "technical_params": {
        "sample_rate": "44100",
        "duration": "30",
        "format": "wav"
      }
    }
  }
  ```

**What it does NOT do:**
- ❌ Call ElevenLabs, Google TTS, or any audio generation API
- ❌ Generate actual audio files
- ❌ Save WAV/MP3 files to disk

## Provider Availability

### Image Providers (Available but Not Used by Roles)

**Files in `/tmp/questfoundry-py/src/questfoundry/providers/image/`:**
- `dalle.py` - DALL-E 3 integration ✅
- `a1111.py` - Automatic1111 (Stable Diffusion) integration ✅
- `imagen.py` - Google Imagen integration ✅

**Status:** These providers exist and likely work, but roles don't use them.

### Audio Providers (Available but Not Used by Roles)

**Files in `/tmp/questfoundry-py/src/questfoundry/providers/audio/`:**
- `elevenlabs.py` - ElevenLabs TTS integration ✅
- `mock.py` - Mock audio provider for testing ✅

**Status:** These providers exist and likely work, but roles don't use them.

## Impact on CLI Integration

### What Works

Our CLI integration successfully:
- ✅ Calls roles via RoleRegistry
- ✅ Passes RoleContext with artifacts
- ✅ Receives RoleResult with success/output
- ✅ Saves artifacts to workspace
- ✅ Displays results to user

### What Doesn't Actually Work

1. **`qf generate image <shotlist-id>`**
   - Calls Illustrator role ✅
   - Illustrator generates JSON spec ✅
   - But no actual image file is created ❌
   - User gets artifact with render specification, not image ❌

2. **`qf generate audio <cuelist-id>`**
   - Calls AudioProducer role ✅
   - AudioProducer generates JSON spec ✅
   - But no actual audio file is created ❌
   - User gets artifact with audio specification, not audio ❌

3. **`qf generate scene <tu-id>`**
   - Calls SceneSmith role ✅
   - SceneSmith generates actual prose ✅
   - Real content is created ✅✅

4. **`qf generate canon <hook-id>`**
   - Calls LoreWeaver role ✅
   - LoreWeaver generates actual lore text ✅
   - Real content is created ✅✅

## Root Cause Analysis

### Design Philosophy

The questfoundry-py library appears to be designed for a **two-stage workflow**:

1. **Planning Stage** (Working)
   - ArtDirector → creates art plans
   - AudioDirector → creates audio plans
   - Plotwright → creates story structure

2. **Execution Stage** (Not Implemented in Roles)
   - Illustrator → *should* generate images from art plans (but doesn't)
   - AudioProducer → *should* generate audio from audio plans (but doesn't)
   - SceneSmith → *actually* generates prose from plot briefs (works!)

### Why Image/Audio Generation is Missing

**Hypothesis:** The library maintainers intentionally separated specification from execution because:
- Image/audio generation is expensive (API costs)
- Generation may require human review/approval
- Different projects may use different providers
- Reproducibility requires deterministic parameters

**Evidence:** Comments in code explicitly say "In a real implementation..." suggesting this is placeholder/stub code.

## Recommendations

### Option 1: Use What Works (Recommended for MVP)

**Focus on text-based generation only:**
- ✅ Keep scene generation (works perfectly)
- ✅ Keep canonization (works perfectly)
- ❌ Disable or document image generation as "spec only"
- ❌ Disable or document audio generation as "spec only"

**Update CLI messaging:**
```bash
qf generate image <shotlist-id>
# Output: "✓ Image specification generated. Use external tools to render."

qf generate scene <tu-id>
# Output: "✓ Scene prose generated successfully."
```

### Option 2: Extend questfoundry-py Roles

**Add image/audio provider support to roles:**
- Modify `Role.__init__()` to accept `ImageProvider` and `AudioProvider`
- Update `Illustrator` to actually call image generation APIs
- Update `AudioProducer` to actually call audio generation APIs

**Effort:** Medium-High (requires changes to questfoundry-py)

### Option 3: Add Media Generation Layer in CLI

**Bypass roles, call providers directly:**
```python
# In CLI: After getting render spec from Illustrator
image_provider = registry.get_image_provider("dalle")
image_data = image_provider.generate_image(
    prompt=render_spec["composition"],
    **render_spec["technical_params"]
)
```

**Effort:** Medium (requires understanding provider APIs)

### Option 4: Document Current State

**Be transparent about limitations:**
- Update docs to explain image/audio are "planning only"
- Mark these features as "Phase 2" or "Coming Soon"
- Focus user attention on working features (scene, lore)

**Effort:** Low (documentation only)

## Testing Verification Commands

```bash
# Test scene generation (should work)
cd /tmp/test-qf-init
qf generate scene TU-001  # Will generate actual prose

# Test image generation (will only generate spec)
qf generate image SHOT-001  # Will generate JSON spec, not image

# Verify what's actually saved
ls .questfoundry/hot/scenes/  # Should have scene artifacts
ls .questfoundry/hot/renders/ # Will have render specs, not images
```

## Conclusion

**Status:** Our CLI integration is working correctly, but questfoundry-py's Illustrator and AudioProducer roles are intentionally incomplete. They generate specifications, not actual media files.

**Recommendation:** Document this limitation clearly and focus on the working text-based generation (scenes, lore) which is fully functional and impressive. Image/audio generation can be a future enhancement when questfoundry-py is updated or when we implement Option 2 or 3.
