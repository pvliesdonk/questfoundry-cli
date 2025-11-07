"""Tests for validation commands"""

import json

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_validate_file_with_valid_artifact(tmp_path):
    """Test validating a valid artifact file"""
    # Create a valid codex entry
    artifact = {
        "title": "Test Entry",
        "slug": "test-entry",
        "locale": "EN",
        "owner": "Codex Curator",
        "edited": "2025-11-07",
        "snapshot": "Cold @ 2025-11-04",
        "tu": "TU-2025-11-07-CC01",
        "lineage": "From canon TU-2025-11-03-LW10; posture plausible",
        "overview": "A test codex entry for validation testing purposes",
        "context": "This entry is used to validate the schema validation system",
        "variants": [
            {
                "variant": "Test Variant",
                "register_region": "neutral",
                "translator_notes": "Translation note for testing"
            }
        ],
        "relations": ["test-relation"],
        "reading_level": "plain",
        "anchor_slug": "/codex/test-entry",
        "from_canon": "Test canon description for validation",
        "research_posture_touched": "plausible",
        "done_checklist": [
            "Player-safe",
            "Links resolve",
            "Variants listed",
            "Relations noted",
            "Register chosen",
            "Anchor set",
            "Canon distilled",
            "Posture logged"
        ]
    }

    artifact_file = tmp_path / "test_entry.json"
    with open(artifact_file, "w") as f:
        json.dump(artifact, f)

    # Validate
    result = runner.invoke(
        app, ["validate", "file", str(artifact_file), "--schema", "codex_entry"]
    )

    assert result.exit_code == 0
    assert "✓" in result.stdout
    assert "valid" in result.stdout.lower()


def test_validate_file_with_invalid_artifact(tmp_path):
    """Test validating an invalid artifact file"""
    # Create an invalid codex entry (missing required fields)
    artifact = {
        "title": "Test Entry",
        "slug": "test-entry",
        # Missing many required fields like locale, owner, edited, etc.
    }

    artifact_file = tmp_path / "test_entry.json"
    with open(artifact_file, "w") as f:
        json.dump(artifact, f)

    # Validate
    result = runner.invoke(
        app, ["validate", "file", str(artifact_file), "--schema", "codex_entry"]
    )

    assert result.exit_code == 1
    assert "✗" in result.stdout
    assert "failed" in result.stdout.lower()


def test_validate_file_nonexistent(tmp_path):
    """Test validating a nonexistent file"""
    result = runner.invoke(
        app,
        [
            "validate",
            "file",
            str(tmp_path / "nonexistent.json"),
            "--schema",
            "codex_entry",
        ],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_validate_file_invalid_json(tmp_path):
    """Test validating a file with invalid JSON"""
    artifact_file = tmp_path / "invalid.json"
    with open(artifact_file, "w") as f:
        f.write("{invalid json")

    result = runner.invoke(
        app, ["validate", "file", str(artifact_file), "--schema", "codex_entry"]
    )

    assert result.exit_code == 1
    assert "json" in result.stdout.lower()


def test_validate_artifact_not_in_project(tmp_path, monkeypatch):
    """Test validating artifact without a project"""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate", "artifact", "test-artifact"])

    assert result.exit_code == 1
    assert "No project found" in result.stdout


def test_validate_artifact_in_project(tmp_path, monkeypatch, mock_questionary_init):
    """Test validating an artifact in a project"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Create a valid codex entry in workspace
    workspace = tmp_path / ".questfoundry"
    codex_dir = workspace / "hot" / "codex"
    codex_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "type": "codex_entry",  # Add type for auto-detection
        "title": "Test Entry",
        "slug": "test-entry",
        "locale": "EN",
        "owner": "Codex Curator",
        "edited": "2025-11-07",
        "snapshot": "Cold @ 2025-11-04",
        "tu": "TU-2025-11-07-CC01",
        "lineage": "From canon TU-2025-11-03-LW10; posture plausible",
        "overview": "A test codex entry for validation testing purposes",
        "context": "This entry is used to validate the schema validation system",
        "variants": [
            {
                "variant": "Test Variant",
                "register_region": "neutral",
                "translator_notes": "Translation note for testing"
            }
        ],
        "relations": ["test-relation"],
        "reading_level": "plain",
        "anchor_slug": "/codex/test-entry",
        "from_canon": "Test canon description for validation",
        "research_posture_touched": "plausible",
        "done_checklist": [
            "Player-safe",
            "Links resolve",
            "Variants listed",
            "Relations noted",
            "Register chosen",
            "Anchor set",
            "Canon distilled",
            "Posture logged"
        ]
    }

    with open(codex_dir / "test-entry.json", "w") as f:
        json.dump(artifact, f)

    # Validate (schema should be auto-detected from type field)
    result = runner.invoke(app, ["validate", "artifact", "test-entry"])

    assert result.exit_code == 0
    assert "✓" in result.stdout
    assert "valid" in result.stdout.lower()


def test_validate_artifact_missing_type_field(
    tmp_path, monkeypatch, mock_questionary_init
):
    """Test validating artifact without type field and no schema specified"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Create artifact without type field
    workspace = tmp_path / ".questfoundry"
    hooks_dir = workspace / "hot" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "id": "test-hook-001",
        "title": "Test Hook",
        # No type field
    }

    with open(hooks_dir / "test-hook-001.json", "w") as f:
        json.dump(artifact, f)

    # Validate without schema
    result = runner.invoke(app, ["validate", "artifact", "test-hook-001"])

    assert result.exit_code == 1
    assert "no 'type' field" in result.stdout.lower()


def test_validate_envelope_shows_coming_soon(tmp_path):
    """Test that envelope validation shows coming soon message"""
    artifact_file = tmp_path / "envelope.json"
    artifact_file.touch()

    result = runner.invoke(app, ["validate", "envelope", str(artifact_file)])

    assert "coming soon" in result.stdout.lower()
