"""Tests for CLI main functionality"""

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_version():
    """Test version command"""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "questfoundry-cli" in result.stdout or "0.1.0" in result.stdout


def test_help():
    """Test help command"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "schema" in result.stdout
    assert "validate" in result.stdout
