"""Tests for qf show command"""

from pathlib import Path

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_show_fails_without_project(tmp_path, monkeypatch):
    """Test that show fails when no project exists"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Run show command
    result = runner.invoke(app, ["show", "test-artifact"])

    # Should fail
    assert result.exit_code == 1
    assert "No project found" in result.stdout


def test_show_fails_with_nonexistent_artifact(tmp_path, monkeypatch):
    """Test that show fails when artifact doesn't exist"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Create minimal project
    (tmp_path / "test.qfproj").touch()
    workspace = tmp_path / ".questfoundry"
    workspace.mkdir()
    (workspace / "hot").mkdir()

    # Run show command with non-existent artifact
    result = runner.invoke(app, ["show", "nonexistent"])

    # Should fail
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()
