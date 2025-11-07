import pytest
from typer.testing import CliTestClient
from qf.cli import app

client = CliTestClient(app)

def test_schema_list():
    result = client.invoke(app, ["schema", "list"])
    assert result.exit_code == 0
    # Will populate with actual schemas
    