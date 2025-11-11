"""Tests for generate command."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from qf.cli import app
from qf.commands import generate

runner = CliRunner()


@pytest.fixture
def mock_role_execution(monkeypatch):
    """Mock questfoundry-py role execution for testing."""
    # Mock successful role execution
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.error = None
    mock_result.output = "Generated content"

    # Mock artifacts
    mock_artifact = MagicMock()
    mock_artifact.artifact_id = "generated-001"
    mock_result.artifacts = [mock_artifact]

    # Mock role
    mock_role = MagicMock()
    mock_role.execute_task.return_value = mock_result

    # Mock role registry
    mock_registry = MagicMock()
    mock_registry.get_role.return_value = mock_role

    # Mock workspace
    mock_workspace = MagicMock()
    mock_workspace.path = Path("/tmp/test")
    mock_workspace.save_hot_artifact = MagicMock()
    mock_workspace.list_hot_artifacts = MagicMock(return_value=[])

    # Patch the utility functions
    monkeypatch.setattr("qf.commands.generate.get_workspace", lambda: mock_workspace)
    monkeypatch.setattr("qf.commands.generate.get_role_registry", lambda: mock_registry)

    return {
        "result": mock_result,
        "role": mock_role,
        "registry": mock_registry,
        "workspace": mock_workspace,
    }


@pytest.fixture
def temp_project():
    """Create a temporary project with workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create project file
        project_file = tmpdir_path / "test.qfproj"
        project_file.write_text("name: Test Project\n")

        # Create workspace
        workspace = tmpdir_path / ".questfoundry"
        workspace.mkdir()
        hot = workspace / "hot"
        hot.mkdir()

        # Create artifact directories
        shotlists_dir = hot / "shotlists"
        shotlists_dir.mkdir()
        audio_dir = hot / "audio"
        audio_dir.mkdir()
        tus_dir = hot / "tus"
        tus_dir.mkdir()
        hooks_dir = hot / "hooks"
        hooks_dir.mkdir()

        # Save current directory and change to temp
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir_path)

        yield tmpdir_path

        # Restore directory
        os.chdir(old_cwd)


@pytest.fixture
def shotlist_artifact(temp_project):
    """Create a test shotlist artifact."""
    artifact = {
        "id": "SHOT-001",
        "type": "shotlist",
        "title": "Lighthouse Scene",
        "status": "draft",
        "description": "Visual shots for lighthouse scene",
        "shots": [
            {"id": "S1", "description": "Wide shot of lighthouse at dusk"},
            {"id": "S2", "description": "Close-up of keeper's face"},
        ]
    }

    artifact_file = (
        temp_project / ".questfoundry" / "hot" / "shotlists" / "SHOT-001.json"
    )
    artifact_file.write_text(json.dumps(artifact))

    return artifact


@pytest.fixture
def cuelist_artifact(temp_project):
    """Create a test cuelist artifact."""
    artifact = {
        "id": "CUE-001",
        "type": "cuelist",
        "title": "Lighthouse Audio Cues",
        "status": "draft",
        "description": "Audio cues for lighthouse scene",
        "cues": [
            {"id": "C1", "description": "Foghorn in distance"},
            {"id": "C2", "description": "Wind howling"},
        ]
    }

    artifact_file = temp_project / ".questfoundry" / "hot" / "audio" / "CUE-001.json"
    artifact_file.write_text(json.dumps(artifact))

    return artifact


@pytest.fixture
def tu_artifact(temp_project):
    """Create a test TU artifact."""
    artifact = {
        "id": "TU-001",
        "type": "tu",
        "title": "The Lighthouse Keeper",
        "status": "draft",
        "description": "Main turning unit for lighthouse story",
        "loop": "story-spark",
    }

    artifact_file = temp_project / ".questfoundry" / "hot" / "tus" / "TU-001.json"
    artifact_file.write_text(json.dumps(artifact))

    return artifact


@pytest.fixture
def hook_artifact(temp_project):
    """Create a test hook artifact."""
    artifact = {
        "id": "HOOK-001",
        "type": "hook",
        "title": "The Lighthouse Keeper's Secret",
        "status": "proposed",
        "description": "A hook about the lighthouse keeper's hidden past",
        "stakes": 4,
    }

    artifact_file = temp_project / ".questfoundry" / "hot" / "hooks" / "HOOK-001.json"
    artifact_file.write_text(json.dumps(artifact))

    return artifact


def test_generate_command_group_exists():
    """Test that generate command group is properly defined."""
    assert generate.app is not None
    assert hasattr(generate, "generate_image")
    assert hasattr(generate, "generate_audio")
    assert hasattr(generate, "generate_scene")
    assert hasattr(generate, "generate_canon")
    assert hasattr(generate, "generate_images")


def test_generate_image_no_project():
    """Test generate image without a project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            result = runner.invoke(app, ["generate", "image", "SHOT-001"])
            assert result.exit_code == 1
            assert "No project found" in result.stdout
        finally:
            os.chdir(old_cwd)


def test_generate_image_artifact_not_found(temp_project):
    """Test generate image when artifact doesn't exist."""
    result = runner.invoke(app, ["generate", "image", "NONEXISTENT"])
    assert result.exit_code == 1
    assert "Artifact not found" in result.stdout


def test_generate_image_wrong_artifact_type(temp_project, tu_artifact):
    """Test generate image with wrong artifact type."""
    result = runner.invoke(app, ["generate", "image", "TU-001"])
    assert result.exit_code == 1
    assert "Expected artifact type" in result.stdout


def test_generate_image_success(temp_project, shotlist_artifact, mock_role_execution):
    """Test successful image generation."""
    result = runner.invoke(app, ["generate", "image", "SHOT-001"])
    assert result.exit_code == 0
    assert "Generated successfully" in result.stdout
    assert "SHOT-001" in result.stdout


def test_generate_image_with_provider(
    temp_project, shotlist_artifact, mock_role_execution
):
    """Test image generation with provider override."""
    result = runner.invoke(
        app, ["generate", "image", "SHOT-001", "--provider", "dalle"]
    )
    assert result.exit_code == 0
    assert "Provider: dalle" in result.stdout


def test_generate_image_with_model(
    temp_project, shotlist_artifact, mock_role_execution
):
    """Test image generation with model override."""
    result = runner.invoke(
        app, ["generate", "image", "SHOT-001", "--model", "dall-e-3"]
    )
    assert result.exit_code == 0
    assert "Model: dall-e-3" in result.stdout


def test_generate_image_with_provider_and_model(
    temp_project, shotlist_artifact, mock_role_execution
):
    """Test image generation with both provider and model."""
    result = runner.invoke(
        app,
        ["generate", "image", "SHOT-001", "--provider", "dalle", "--model", "dall-e-3"],
    )
    assert result.exit_code == 0
    assert "Provider: dalle" in result.stdout
    assert "Model: dall-e-3" in result.stdout


def test_generate_audio_no_project():
    """Test generate audio without a project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            result = runner.invoke(app, ["generate", "audio", "CUE-001"])
            assert result.exit_code == 1
            assert "No project found" in result.stdout
        finally:
            os.chdir(old_cwd)


def test_generate_audio_artifact_not_found(temp_project):
    """Test generate audio when artifact doesn't exist."""
    result = runner.invoke(app, ["generate", "audio", "NONEXISTENT"])
    assert result.exit_code == 1
    assert "Artifact not found" in result.stdout


def test_generate_audio_wrong_artifact_type(temp_project, shotlist_artifact):
    """Test generate audio with wrong artifact type."""
    result = runner.invoke(app, ["generate", "audio", "SHOT-001"])
    assert result.exit_code == 1
    assert "Expected artifact type" in result.stdout


def test_generate_audio_success(temp_project, cuelist_artifact, mock_role_execution):
    """Test successful audio generation."""
    result = runner.invoke(app, ["generate", "audio", "CUE-001"])
    assert result.exit_code == 0
    assert "Generated successfully" in result.stdout


def test_generate_audio_with_provider(
    temp_project, cuelist_artifact, mock_role_execution
):
    """Test audio generation with provider override."""
    result = runner.invoke(
        app, ["generate", "audio", "CUE-001", "--provider", "elevenlabs"]
    )
    assert result.exit_code == 0
    assert "Provider: elevenlabs" in result.stdout


def test_generate_scene_no_project():
    """Test generate scene without a project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            result = runner.invoke(app, ["generate", "scene", "TU-001"])
            assert result.exit_code == 1
            assert "No project found" in result.stdout
        finally:
            os.chdir(old_cwd)


def test_generate_scene_artifact_not_found(temp_project):
    """Test generate scene when artifact doesn't exist."""
    result = runner.invoke(app, ["generate", "scene", "NONEXISTENT"])
    assert result.exit_code == 1
    assert "Artifact not found" in result.stdout


def test_generate_scene_wrong_artifact_type(temp_project, hook_artifact):
    """Test generate scene with wrong artifact type."""
    result = runner.invoke(app, ["generate", "scene", "HOOK-001"])
    assert result.exit_code == 1
    assert "Expected artifact type" in result.stdout


def test_generate_scene_success(temp_project, tu_artifact, mock_role_execution):
    """Test successful scene generation."""
    result = runner.invoke(app, ["generate", "scene", "TU-001"])
    assert result.exit_code == 0
    assert "Generated successfully" in result.stdout


def test_generate_scene_with_provider(temp_project, tu_artifact, mock_role_execution):
    """Test scene generation with provider override."""
    result = runner.invoke(
        app, ["generate", "scene", "TU-001", "--provider", "openai"]
    )
    assert result.exit_code == 0
    assert "Provider: openai" in result.stdout


def test_generate_canon_no_project():
    """Test generate canon without a project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            result = runner.invoke(app, ["generate", "canon", "HOOK-001"])
            assert result.exit_code == 1
            assert "No project found" in result.stdout
        finally:
            os.chdir(old_cwd)


def test_generate_canon_artifact_not_found(temp_project):
    """Test generate canon when artifact doesn't exist."""
    result = runner.invoke(app, ["generate", "canon", "NONEXISTENT"])
    assert result.exit_code == 1
    assert "Artifact not found" in result.stdout


def test_generate_canon_wrong_artifact_type(temp_project, tu_artifact):
    """Test generate canon with wrong artifact type."""
    result = runner.invoke(app, ["generate", "canon", "TU-001"])
    assert result.exit_code == 1
    assert "Expected artifact type" in result.stdout


def test_generate_canon_success(temp_project, hook_artifact, mock_role_execution):
    """Test successful canonization."""
    result = runner.invoke(app, ["generate", "canon", "HOOK-001"])
    assert result.exit_code == 0
    assert "Generated successfully" in result.stdout


def test_generate_canon_with_provider(temp_project, hook_artifact, mock_role_execution):
    """Test canonization with provider override."""
    result = runner.invoke(
        app, ["generate", "canon", "HOOK-001", "--provider", "openai"]
    )
    assert result.exit_code == 0
    assert "Provider: openai" in result.stdout


def test_generate_images_batch_no_project():
    """Test batch image generation without a project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            result = runner.invoke(app, ["generate", "images", "--pending"])
            assert result.exit_code == 1
            assert "No project found" in result.stdout
        finally:
            os.chdir(old_cwd)


def test_generate_images_batch_no_pending_flag(temp_project):
    """Test batch image generation without --pending flag."""
    result = runner.invoke(app, ["generate", "images"])
    assert result.exit_code == 1
    assert "Please specify --pending" in result.stdout


def test_generate_images_batch_success(temp_project, mock_role_execution):
    """Test successful batch image generation."""
    # Mock workspace to return pending shotlists as Artifact-like objects
    mock_workspace = mock_role_execution["workspace"]

    # Create mock artifacts with proper attributes
    mock_shotlists = []
    for i in range(1, 4):
        mock_shotlist = MagicMock()
        mock_shotlist.artifact_id = f"SHOT-00{i}"
        mock_shotlist.type = "shotlist"
        mock_shotlists.append(mock_shotlist)

    mock_workspace.list_hot_artifacts.return_value = mock_shotlists

    result = runner.invoke(app, ["generate", "images", "--pending"])
    assert result.exit_code == 0
    assert "Batch generation complete" in result.stdout
    assert "Generated: 3 image(s)" in result.stdout


def test_generate_images_batch_with_provider(temp_project, mock_role_execution):
    """Test batch image generation with provider override."""
    # Mock workspace to return pending shotlists as Artifact-like objects
    mock_workspace = mock_role_execution["workspace"]

    mock_shotlist = MagicMock()
    mock_shotlist.artifact_id = "SHOT-001"
    mock_shotlist.type = "shotlist"
    mock_workspace.list_hot_artifacts.return_value = [mock_shotlist]

    result = runner.invoke(
        app, ["generate", "images", "--pending", "--provider", "midjourney"]
    )
    assert result.exit_code == 0
    assert "Provider: midjourney" in result.stdout


def test_generate_images_batch_with_provider_and_model(
    temp_project, mock_role_execution
):
    """Test batch image generation with both provider and model."""
    # Mock workspace to return pending shotlists as Artifact-like objects
    mock_workspace = mock_role_execution["workspace"]

    mock_shotlist = MagicMock()
    mock_shotlist.artifact_id = "SHOT-001"
    mock_shotlist.type = "shotlist"
    mock_workspace.list_hot_artifacts.return_value = [mock_shotlist]

    result = runner.invoke(
        app,
        [
            "generate",
            "images",
            "--pending",
            "--provider",
            "dalle",
            "--model",
            "dall-e-3",
        ],
    )
    assert result.exit_code == 0
    assert "Provider: dalle" in result.stdout
    assert "Model: dall-e-3" in result.stdout


def test_find_artifact_in_hot_directory(temp_project, shotlist_artifact):
    """Test finding an artifact in the hot directory."""
    artifact = generate.find_artifact("SHOT-001")
    assert artifact is not None
    assert artifact.exists()
    assert artifact.name == "SHOT-001.json"


def test_find_artifact_by_id_in_content(temp_project):
    """Test finding an artifact by ID in file content."""
    # Create artifact with mismatched filename
    artifact_data = {
        "id": "SHOT-002",
        "type": "shotlist",
        "title": "Test",
    }

    artifact_file = temp_project / ".questfoundry" / "hot" / "shotlists" / "other.json"
    artifact_file.write_text(json.dumps(artifact_data))

    # Should still find it by ID
    artifact = generate.find_artifact("SHOT-002")
    assert artifact is not None


def test_load_artifact(temp_project, shotlist_artifact):
    """Test loading an artifact."""
    artifact = generate.load_artifact("SHOT-001")
    assert artifact is not None
    assert artifact["id"] == "SHOT-001"
    assert artifact["type"] == "shotlist"


def test_load_artifact_not_found(temp_project):
    """Test loading a non-existent artifact."""
    artifact = generate.load_artifact("NONEXISTENT")
    assert artifact is None


def test_validate_artifact_type_valid(temp_project, shotlist_artifact):
    """Test artifact type validation with valid type."""
    is_valid, artifact = generate.validate_artifact_type("SHOT-001", ["shotlist"])
    assert is_valid is True
    assert artifact is not None


def test_validate_artifact_type_invalid_type(temp_project, shotlist_artifact):
    """Test artifact type validation with invalid type."""
    is_valid, artifact = generate.validate_artifact_type("SHOT-001", ["tu"])
    assert is_valid is False
    assert artifact is None


def test_validate_artifact_type_not_found(temp_project):
    """Test artifact type validation when artifact doesn't exist."""
    is_valid, artifact = generate.validate_artifact_type("NONEXISTENT", ["shotlist"])
    assert is_valid is False
    assert artifact is None
