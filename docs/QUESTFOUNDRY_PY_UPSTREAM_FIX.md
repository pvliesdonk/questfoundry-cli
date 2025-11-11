# questfoundry-py Upstream Fix Guide

## Problem Statement

**Current State:** Illustrator and AudioProducer roles only generate JSON specifications, not actual media files.

**Root Cause:** `Role.__init__()` only accepts `TextProvider`, preventing roles from accessing image/audio generation capabilities.

**Goal:** Enable Illustrator and AudioProducer to generate actual media files using existing ImageProvider and AudioProvider infrastructure.

---

## Architecture Overview

### Current Architecture (Broken)

```
┌─────────────────┐
│  RoleRegistry   │
├─────────────────┤
│ - text_provider │──┐
│ - image_provider│  │  ✗ Not passed to roles!
│ - audio_provider│  │  ✗ Not passed to roles!
└─────────────────┘  │
                     │
                     ▼
              ┌─────────────┐
              │    Role     │
              ├─────────────┤
              │ - provider  │ ◄── Only TextProvider
              └─────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ Illustrator  │──► Generates JSON spec only
              └──────────────┘
```

### Proposed Architecture (Fixed)

```
┌─────────────────┐
│  RoleRegistry   │
├─────────────────┤
│ - text_provider │──┐
│ - image_provider│──┼─► Pass to roles
│ - audio_provider│──┘
└─────────────────┘
                     │
                     ▼
              ┌─────────────────────────┐
              │         Role            │
              ├─────────────────────────┤
              │ - text_provider         │ ◄── Text LLM
              │ - image_provider (opt)  │ ◄── Image generation
              │ - audio_provider (opt)  │ ◄── Audio generation
              └─────────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ Illustrator  │──► Generates actual images
              └──────────────┘
```

---

## Required Changes

### 1. Update Role Base Class

**File:** `src/questfoundry/roles/base.py` (lines 85-93)

**Current:**
```python
def __init__(
    self,
    provider: TextProvider,
    spec_path: Path | None = None,
    config: dict[str, Any] | None = None,
    session: "RoleSession | None" = None,
    human_callback: "HumanCallback | None" = None,
    role_config: dict[str, Any] | None = None,
):
```

**Proposed:**
```python
def __init__(
    self,
    provider: TextProvider,
    spec_path: Path | None = None,
    config: dict[str, Any] | None = None,
    session: "RoleSession | None" = None,
    human_callback: "HumanCallback | None" = None,
    role_config: dict[str, Any] | None = None,
    image_provider: "ImageProvider | None" = None,  # NEW
    audio_provider: "AudioProvider | None" = None,  # NEW
):
    """
    Initialize role with providers and configuration.

    Args:
        provider: Text provider for LLM interactions (required)
        image_provider: Optional image generation provider
        audio_provider: Optional audio generation provider
        ...
    """
    self.provider = provider
    self.image_provider = image_provider  # NEW
    self.audio_provider = audio_provider  # NEW
    # ... rest of init
```

**Imports to add:**
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..providers.base import ImageProvider, AudioProvider
```

---

### 2. Update RoleRegistry

**File:** `src/questfoundry/roles/registry.py` (lines 139-192)

**Current:**
```python
def get_role(self, role_name: str) -> Role:
    """Get a role instance by name."""
    # ... validation ...

    text_provider = self.provider_registry.get_text_provider(...)

    return role_class(
        provider=text_provider,
        spec_path=self.spec_path,
        # ... other args
    )
```

**Proposed:**
```python
def get_role(self, role_name: str) -> Role:
    """Get a role instance by name."""
    # ... validation ...

    text_provider = self.provider_registry.get_text_provider(...)

    # NEW: Get image/audio providers if available
    image_provider = None
    audio_provider = None

    try:
        image_provider = self.provider_registry.get_image_provider()
    except Exception:
        # Image provider not configured, role will work without it
        pass

    try:
        audio_provider = self.provider_registry.get_audio_provider()
    except Exception:
        # Audio provider not configured, role will work without it
        pass

    return role_class(
        provider=text_provider,
        spec_path=self.spec_path,
        image_provider=image_provider,  # NEW
        audio_provider=audio_provider,  # NEW
        # ... other args
    )
```

---

### 3. Update Illustrator Role

**File:** `src/questfoundry/roles/illustrator.py` (lines 71-132)

**Current Implementation (Spec Generation Only):**
```python
def _create_render(self, context: RoleContext) -> RoleResult:
    """Produce illustration from art plan."""
    system_prompt = self.build_system_prompt(context)
    art_plan = context.additional_context.get("art_plan", {})

    # Asks LLM to generate JSON spec describing the image
    user_prompt = f"""# Task: Create Render
    ...
    Note: In a real implementation, this would interface with image generation.
    For now, provide a detailed rendering specification.
    ...
    """

    response = self._call_llm(system_prompt, user_prompt, max_tokens=1500)
    data = self._parse_json_from_response(response)

    return RoleResult(
        success=True,
        output=response,
        metadata={
            "content_type": "render",
            "render_spec": data.get("render_spec", {}),
        },
    )
```

**Proposed Implementation (Actual Image Generation):**
```python
def _create_render(self, context: RoleContext) -> RoleResult:
    """Produce illustration from art plan."""

    # Check if image provider is available
    if not self.image_provider:
        # Fallback to spec generation if no provider
        return self._generate_render_spec(context)

    # Extract art plan and composition details
    art_plan = context.additional_context.get("art_plan", {})
    shotlist = context.artifacts[0] if context.artifacts else None

    # Step 1: Use text LLM to refine the prompt for image generation
    system_prompt = self.build_system_prompt(context)

    user_prompt = f"""# Task: Create Image Generation Prompt

{self.format_artifacts(context.artifacts)}

## Art Plan
{self._format_dict(art_plan)}

Based on the art plan, create a detailed prompt for image generation that includes:
- Main subject and action
- Composition and framing
- Lighting and mood
- Style and artistic approach
- Technical requirements (aspect ratio, etc.)

Respond with a single, detailed prompt suitable for DALL-E, Midjourney, or Stable Diffusion.
Keep it under 400 characters but make it rich with visual detail.
"""

    try:
        # Generate optimized prompt using text LLM
        image_prompt = self._call_llm(
            system_prompt, user_prompt, max_tokens=500
        ).strip()

        # Step 2: Generate actual image using ImageProvider
        image_result = self.image_provider.generate_image(
            prompt=image_prompt,
            width=art_plan.get("width", 1024),
            height=art_plan.get("height", 1024),
            # Optional: Pass seed for determinism
            seed=art_plan.get("seed"),
        )

        # Step 3: Save image to workspace if path provided
        image_path = None
        if context.workspace_path:
            renders_dir = context.workspace_path / ".questfoundry" / "hot" / "renders"
            renders_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            render_id = art_plan.get("render_id") or f"render-{int(time.time())}"
            image_path = renders_dir / f"{render_id}.png"

            # Save image data
            with open(image_path, "wb") as f:
                f.write(image_result)

        # Step 4: Create artifact with render metadata
        from questfoundry.models import Artifact

        render_artifact = Artifact(
            type="render",
            data={
                "render_id": render_id,
                "prompt": image_prompt,
                "width": art_plan.get("width", 1024),
                "height": art_plan.get("height", 1024),
                "art_plan_id": art_plan.get("art_plan_id"),
                "image_path": str(image_path) if image_path else None,
            },
            metadata={
                "id": render_id,
                "generated_by": "illustrator",
                "provider": self.image_provider.__class__.__name__,
            },
        )

        return RoleResult(
            success=True,
            output=f"Generated image: {image_prompt}",
            artifacts=[render_artifact],
            metadata={
                "content_type": "render",
                "image_prompt": image_prompt,
                "image_path": str(image_path) if image_path else None,
                "image_size": len(image_result),
            },
        )

    except Exception as e:
        return RoleResult(
            success=False,
            output="",
            error=f"Error creating render: {e}",
        )

def _generate_render_spec(self, context: RoleContext) -> RoleResult:
    """Fallback: Generate specification when no image provider available."""
    # Keep existing spec generation code here
    system_prompt = self.build_system_prompt(context)
    art_plan = context.additional_context.get("art_plan", {})

    user_prompt = f"""# Task: Create Render Specification

{self.format_artifacts(context.artifacts)}

## Art Plan
{self._format_dict(art_plan)}

Since image generation is not available, provide a detailed specification
that describes what the render should look like.

Respond in JSON format:
```json
{{
  "render_spec": {{
    "composition": "Detailed composition description",
    "style_notes": "How house style is reflected",
    "technical_params": {{
      "seed": "deterministic seed if applicable",
      "aspect_ratio": "ratio",
      "palette": ["color1", "color2"]
    }}
  }},
  "alt_text": "Accessibility description",
  "note": "Specification only - use external tools to generate actual image"
}}
```
"""

    response = self._call_llm(system_prompt, user_prompt, max_tokens=1500)
    data = self._parse_json_from_response(response)

    return RoleResult(
        success=True,
        output=response,
        metadata={
            "content_type": "render_spec",
            "render_spec": data.get("render_spec", {}),
            "note": "Specification only - image provider not configured",
        },
    )
```

---

### 4. Update AudioProducer Role

**File:** `src/questfoundry/roles/audio_producer.py` (lines 71-135)

**Similar pattern to Illustrator:**

```python
def _create_asset(self, context: RoleContext) -> RoleResult:
    """Produce audio from plan."""

    # Check if audio provider is available
    if not self.audio_provider:
        # Fallback to spec generation if no provider
        return self._generate_audio_spec(context)

    audio_plan = context.additional_context.get("audio_plan", {})

    try:
        # Step 1: Use text LLM to refine script/description for TTS
        system_prompt = self.build_system_prompt(context)

        user_prompt = f"""# Task: Prepare Audio Script

{self.format_artifacts(context.artifacts)}

## Audio Plan
{self._format_dict(audio_plan)}

Prepare the text/script for audio generation based on the plan.
If it's voice-over, provide the exact text to be spoken.
If it's sound effect, provide a detailed description.

Keep it concise and suitable for TTS or audio generation.
"""

        audio_script = self._call_llm(
            system_prompt, user_prompt, max_tokens=500
        ).strip()

        # Step 2: Generate actual audio using AudioProvider
        audio_result = self.audio_provider.generate_audio(
            text=audio_script,
            voice=audio_plan.get("voice", "narrator"),
            # Optional parameters
            speed=audio_plan.get("speed", 1.0),
        )

        # Step 3: Save audio to workspace
        audio_path = None
        if context.workspace_path:
            audio_dir = context.workspace_path / ".questfoundry" / "hot" / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            asset_id = audio_plan.get("asset_id") or f"audio-{int(time.time())}"
            audio_path = audio_dir / f"{asset_id}.mp3"

            with open(audio_path, "wb") as f:
                f.write(audio_result)

        # Step 4: Create artifact
        from questfoundry.models import Artifact

        audio_artifact = Artifact(
            type="audio_asset",
            data={
                "asset_id": asset_id,
                "script": audio_script,
                "audio_plan_id": audio_plan.get("audio_plan_id"),
                "audio_path": str(audio_path) if audio_path else None,
            },
            metadata={
                "id": asset_id,
                "generated_by": "audio_producer",
                "provider": self.audio_provider.__class__.__name__,
            },
        )

        return RoleResult(
            success=True,
            output=f"Generated audio: {audio_script[:100]}...",
            artifacts=[audio_artifact],
            metadata={
                "content_type": "audio_asset",
                "audio_path": str(audio_path) if audio_path else None,
                "audio_size": len(audio_result),
            },
        )

    except Exception as e:
        return RoleResult(
            success=False,
            output="",
            error=f"Error creating audio asset: {e}",
        )

def _generate_audio_spec(self, context: RoleContext) -> RoleResult:
    """Fallback: Generate specification when no audio provider available."""
    # Keep existing spec generation code
    # Similar to current implementation
```

---

## Testing Strategy

### Unit Tests

**File:** `tests/roles/test_illustrator.py`

```python
def test_illustrator_with_image_provider(mock_image_provider, spec_path):
    """Test Illustrator generates actual images when provider available."""
    illustrator = Illustrator(
        provider=mock_text_provider,
        image_provider=mock_image_provider,
        spec_path=spec_path,
    )

    context = RoleContext(
        task="create_render",
        artifacts=[art_plan_artifact],
        workspace_path=tmp_path,
        additional_context={"art_plan": {...}},
    )

    result = illustrator.execute_task(context)

    assert result.success
    assert len(result.artifacts) > 0
    assert result.artifacts[0].type == "render"
    assert result.metadata["image_path"] is not None

    # Verify image file was created
    image_path = Path(result.metadata["image_path"])
    assert image_path.exists()
    assert image_path.suffix == ".png"


def test_illustrator_without_image_provider(mock_text_provider, spec_path):
    """Test Illustrator falls back to spec generation without provider."""
    illustrator = Illustrator(
        provider=mock_text_provider,
        image_provider=None,  # No provider
        spec_path=spec_path,
    )

    context = RoleContext(
        task="create_render",
        artifacts=[art_plan_artifact],
        additional_context={"art_plan": {...}},
    )

    result = illustrator.execute_task(context)

    assert result.success
    assert result.metadata["content_type"] == "render_spec"
    assert "Specification only" in result.metadata.get("note", "")
```

### Integration Tests

**File:** `tests/integration/test_media_generation.py`

```python
@pytest.mark.integration
def test_full_image_generation_workflow(workspace_path):
    """Test complete workflow from art plan to image file."""
    # Initialize workspace
    ws = WorkspaceManager(workspace_path)
    ws.init_workspace("Test Project")

    # Set up providers
    provider_config = ProviderConfig()
    provider_registry = ProviderRegistry(provider_config)
    role_registry = RoleRegistry(
        provider_registry=provider_registry,
        spec_path=spec_path,
    )

    # Get illustrator (should have image provider)
    illustrator = role_registry.get_role("illustrator")
    assert illustrator.image_provider is not None

    # Execute generation
    result = illustrator.execute_task(RoleContext(
        task="create_render",
        workspace_path=workspace_path,
        # ...
    ))

    assert result.success

    # Verify image file exists
    renders_dir = workspace_path / ".questfoundry" / "hot" / "renders"
    image_files = list(renders_dir.glob("*.png"))
    assert len(image_files) > 0
```

---

## Migration Strategy

### Backward Compatibility

1. **Make providers optional** - Roles should work without image/audio providers (fallback to spec generation)
2. **Detect provider availability** - Check `if self.image_provider` before using it
3. **Clear error messages** - When provider missing, explain what's needed
4. **Gradual rollout** - Update one role at a time, test thoroughly

### Configuration Examples

**File:** `.questfoundry/config.yml`

```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o

  image:
    default: dalle
    dalle:
      api_key: ${OPENAI_API_KEY}
      model: dall-e-3
      size: "1024x1024"

  audio:
    default: elevenlabs
    elevenlabs:
      api_key: ${ELEVENLABS_API_KEY}
      voice: "narrator"
```

---

## Implementation Checklist

- [ ] Update `Role.__init__()` to accept image_provider and audio_provider
- [ ] Update `RoleRegistry.get_role()` to pass providers to roles
- [ ] Update `Illustrator._create_render()` for actual image generation
- [ ] Add `Illustrator._generate_render_spec()` as fallback
- [ ] Update `AudioProducer._create_asset()` for actual audio generation
- [ ] Add `AudioProducer._generate_audio_spec()` as fallback
- [ ] Add unit tests for roles with and without providers
- [ ] Add integration tests for full workflow
- [ ] Update documentation
- [ ] Test with real API keys (DALL-E, ElevenLabs)
- [ ] Handle rate limits and errors gracefully
- [ ] Add logging for debugging

---

## Expected Outcomes

**Before Fix:**
```bash
qf generate image SHOT-001
# Output: JSON spec describing what image should look like
# File: .questfoundry/hot/renders/SHOT-001-spec.json
```

**After Fix:**
```bash
qf generate image SHOT-001
# Output: Actual PNG image file generated via DALL-E
# File: .questfoundry/hot/renders/SHOT-001.png
```

---

## Questions for Discussion

1. **File storage strategy** - Should images be stored in workspace or referenced externally?
2. **Provider selection** - Should roles auto-detect best provider or require explicit config?
3. **Cost concerns** - Image/audio generation is expensive. Add confirmation prompts?
4. **Batch limits** - Limit number of images that can be generated at once?
5. **Caching** - Should generated images be cached to avoid regeneration?

---

## References

- **Current Implementation:** `/tmp/questfoundry-py/src/questfoundry/roles/`
- **Provider Infrastructure:** `/tmp/questfoundry-py/src/questfoundry/providers/`
- **Role Base Class:** `/tmp/questfoundry-py/src/questfoundry/roles/base.py`
- **Registry:** `/tmp/questfoundry-py/src/questfoundry/roles/registry.py`
