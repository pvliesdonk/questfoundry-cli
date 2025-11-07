"""Tests for qf list command"""


from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_list_shows_no_artifacts(tmp_path, monkeypatch):
    """Test list when no artifacts exist"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Create minimal project
    (tmp_path / "test.qfproj").touch()
    workspace = tmp_path / ".questfoundry"
    workspace.mkdir()

    # Run list command
    result = runner.invoke(app, ["list"])

    # Should succeed even with no artifacts
    assert result.exit_code == 0
    assert "No artifacts" in result.stdout or result.stdout.strip() == ""


def test_list_fails_without_project(tmp_path, monkeypatch):
    """Test that list fails when no project exists"""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Run list command
    result = runner.invoke(app, ["list"])

    # Should fail
    assert result.exit_code == 1
    assert "No project found" in result.stdout
