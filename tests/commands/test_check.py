"""Tests for quality check commands"""

import json

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_check_without_project(tmp_path, monkeypatch):
    """Test running checks without a project"""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["check", "run"])

    assert result.exit_code == 1
    assert "No project found" in result.stdout


def test_check_empty_project(tmp_path, monkeypatch, mock_questionary_init):
    """Test running checks on an empty project"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Run checks
    result = runner.invoke(app, ["check", "run"])

    assert result.exit_code == 0
    assert "✓" in result.stdout
    assert "passed" in result.stdout.lower()


def test_check_with_valid_artifacts(tmp_path, monkeypatch, mock_questionary_init):
    """Test running checks with valid artifacts"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Create valid codex entry
    workspace = tmp_path / ".questfoundry"
    codex_dir = workspace / "hot" / "codex"
    codex_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "id": "test-entry",
        "type": "codex_entry",
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

    # Run checks
    result = runner.invoke(app, ["check", "run"])

    assert result.exit_code == 0
    assert "✓" in result.stdout
    assert "PASS" in result.stdout


def test_check_with_invalid_json(tmp_path, monkeypatch, mock_questionary_init):
    """Test running checks with invalid JSON"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Create invalid JSON file
    workspace = tmp_path / ".questfoundry"
    hooks_dir = workspace / "hot" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    with open(hooks_dir / "invalid.json", "w") as f:
        f.write("{invalid json")

    # Run checks
    result = runner.invoke(app, ["check", "run"])

    assert result.exit_code == 1
    assert "✗" in result.stdout
    assert "FAIL" in result.stdout


def test_check_with_missing_required_fields(
    tmp_path, monkeypatch, mock_questionary_init
):
    """Test running checks with missing required fields"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Create artifact without required fields
    workspace = tmp_path / ".questfoundry"
    hooks_dir = workspace / "hot" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "title": "Test Hook",
        # missing 'id' and 'type'
    }

    with open(hooks_dir / "incomplete.json", "w") as f:
        json.dump(artifact, f)

    # Run checks
    result = runner.invoke(app, ["check", "run"])

    assert result.exit_code == 1
    assert "FAIL" in result.stdout


def test_check_with_specific_bars(tmp_path, monkeypatch, mock_questionary_init):
    """Test running specific quality bars"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Run specific bars
    result = runner.invoke(app, ["check", "run", "--bars", "integrity,required"])

    assert result.exit_code == 0
    assert "Integrity" in result.stdout
    assert "Required Fields" in result.stdout


def test_check_with_invalid_bar_name(tmp_path, monkeypatch, mock_questionary_init):
    """Test running checks with invalid bar name"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Try to run invalid bar
    result = runner.invoke(app, ["check", "run", "--bars", "nonexistent"])

    assert result.exit_code == 1
    assert "Invalid quality bars" in result.stdout


def test_check_verbose_shows_errors(tmp_path, monkeypatch, mock_questionary_init):
    """Test that verbose mode shows detailed errors"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Create artifact without required fields
    workspace = tmp_path / ".questfoundry"
    hooks_dir = workspace / "hot" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    artifact = {"title": "Test"}

    with open(hooks_dir / "incomplete.json", "w") as f:
        json.dump(artifact, f)

    # Run checks with verbose
    result = runner.invoke(app, ["check", "run", "--verbose"])

    assert result.exit_code == 1
    assert "Detailed Errors" in result.stdout
    assert "incomplete.json" in result.stdout


def test_check_naming_convention_mismatch(tmp_path, monkeypatch, mock_questionary_init):
    """Test check fails when filename doesn't match artifact ID"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Create artifact with mismatched filename and ID
    workspace = tmp_path / ".questfoundry"
    codex_dir = workspace / "hot" / "codex"
    codex_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "id": "correct-id",
        "type": "codex_entry",
        "title": "Test Entry",
    }

    with open(codex_dir / "wrong-filename.json", "w") as f:
        json.dump(artifact, f)

    # Run checks
    result = runner.invoke(app, ["check", "run"])

    assert result.exit_code == 1
    assert "FAIL" in result.stdout
