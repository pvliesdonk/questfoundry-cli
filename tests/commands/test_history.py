"""Tests for qf history command"""


from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_history_shows_empty_state(tmp_path, monkeypatch):
    """Test history when no TUs exist"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Create minimal project
    (tmp_path / "test.qfproj").touch()
    workspace = tmp_path / ".questfoundry"
    workspace.mkdir()

    # Run history command
    result = runner.invoke(app, ["history"])

    # Should succeed with empty message
    assert result.exit_code == 0
    assert "No history yet" in result.stdout or "TUs will appear" in result.stdout


def test_history_fails_without_project(tmp_path, monkeypatch):
    """Test that history fails when no project exists"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Run history command
    result = runner.invoke(app, ["history"])

    # Should fail
    assert result.exit_code == 1
    assert "No project found" in result.stdout
