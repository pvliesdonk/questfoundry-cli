import pytest
from typer.testing import CliTestClient
from qf.cli import app

client = CliTestClient(app)

def test_version():
    result = client.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "questfoundry-cli" in result.stdout

def test_help():
    result = client.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "schema" in result.stdout
    assert "validate" in result.stdout
    