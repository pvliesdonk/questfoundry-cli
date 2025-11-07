"""Tests for provider commands"""

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_provider_list_in_project(tmp_path, monkeypatch, mock_questionary_init):
    """Test listing providers in a project"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # List providers
    result = runner.invoke(app, ["provider", "list"])
    assert result.exit_code == 0
    assert "Available Providers" in result.stdout
    assert "OpenAI" in result.stdout
    assert "Anthropic" in result.stdout
    assert "text" in result.stdout


def test_provider_list_without_project(tmp_path, monkeypatch):
    """Test listing providers without a project"""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["provider", "list"])
    assert result.exit_code == 1
    assert "No project found" in result.stdout


def test_provider_list_shows_default(tmp_path, monkeypatch, mock_questionary_init):
    """Test that provider list shows the default provider"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # List providers
    result = runner.invoke(app, ["provider", "list"])
    assert result.exit_code == 0

    # Check that openai is marked as default (from template config)
    lines = result.stdout.split("\n")
    # Find the OpenAI row and check for checkmark in Default column
    for line in lines:
        if "OpenAI" in line and "text" in line:
            assert "✓" in line


def test_provider_list_shows_configured_status(
    tmp_path, monkeypatch, mock_questionary_init
):
    """Test that provider list shows configured status"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Configure OpenAI provider
    result = runner.invoke(
        app, ["config", "set", "providers.text.openai.api_key", "sk-test"]
    )
    assert result.exit_code == 0

    # List providers
    result = runner.invoke(app, ["provider", "list"])
    assert result.exit_code == 0

    # OpenAI should show as configured
    assert "✓ configured" in result.stdout or "configured" in result.stdout
