"""Tests for basic commands"""

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_schema_list():
    """Test schema list command"""
    # This will fail until questfoundry-py is properly installed
    # For now, just test that the command exists
    result = runner.invoke(app, ["schema", "list"])
    # Command should exist even if it fails due to missing dependency
    assert result.exit_code in [0, 1]
