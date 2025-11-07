"""Tests for qf init command"""

import json
from pathlib import Path

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_init_creates_project(tmp_path, monkeypatch):
    """Test that init creates a new project"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Mock questionary.text to auto-respond
    import questionary

    original_text = questionary.text

    def mock_text(message, **kwargs):
        if "name" in message.lower():
            result = original_text(message, **kwargs)
            result.ask = lambda: "test-project"
            return result
        elif "description" in message.lower():
            result = original_text(message, **kwargs)
            result.ask = lambda: "Test description"
            return result
        return original_text(message, **kwargs)

    monkeypatch.setattr(questionary, "text", mock_text)

    # Run init command
    result = runner.invoke(app, ["init"])

    # Check exit code
    assert result.exit_code == 0

    # Check that project file was created
    project_file = tmp_path / "test-project.qfproj"
    assert project_file.exists()

    # Check workspace was created
    workspace = tmp_path / ".questfoundry"
    assert workspace.exists()
    assert (workspace / "hot").exists()
    assert (workspace / "config.yml").exists()

    # Verify project metadata
    with open(project_file) as f:
        metadata = json.load(f)
        assert metadata["name"] == "test-project"
        assert metadata["description"] == "Test description"


def test_init_fails_in_existing_project(tmp_path, monkeypatch):
    """Test that init fails if project already exists"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Create existing project file
    (tmp_path / "existing.qfproj").touch()

    # Run init command
    result = runner.invoke(app, ["init"])

    # Should fail
    assert result.exit_code == 1
    assert "already exists" in result.stdout.lower()
