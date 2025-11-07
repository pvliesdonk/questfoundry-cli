"""Tests for qf status command"""

import json

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_status_shows_project_info(tmp_path, monkeypatch):
    """Test that status displays project information"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Create a project file
    project_file = tmp_path / "test.qfproj"
    metadata = {
        "name": "test-project",
        "description": "Test description",
        "version": "0.1.0",
    }
    with open(project_file, "w") as f:
        json.dump(metadata, f)

    # Create workspace
    workspace = tmp_path / ".questfoundry"
    workspace.mkdir()

    # Run status command
    result = runner.invoke(app, ["status"])

    # Check output
    assert result.exit_code == 0
    assert "test-project" in result.stdout
    assert "Test description" in result.stdout


def test_status_fails_without_project(tmp_path, monkeypatch):
    """Test that status fails when no project exists"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Run status command
    result = runner.invoke(app, ["status"])

    # Should fail
    assert result.exit_code == 1
    assert "No project found" in result.stdout
