"""Tests for config commands"""

from pathlib import Path

import yaml
from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_config_list_in_project(tmp_path, monkeypatch, mock_questionary_init):
    """Test listing config in a project"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # List config
    result = runner.invoke(app, ["config", "list"])
    assert result.exit_code == 0
    assert "Configuration" in result.stdout
    assert "providers" in result.stdout
    assert "ui" in result.stdout


def test_config_list_without_project(tmp_path, monkeypatch):
    """Test listing config without a project"""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["config", "list"])
    assert result.exit_code == 1
    assert "No project found" in result.stdout


def test_config_get_existing_key(tmp_path, monkeypatch, mock_questionary_init):
    """Test getting an existing config key"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Get a config value
    result = runner.invoke(app, ["config", "get", "ui.color"])
    assert result.exit_code == 0
    assert "ui.color" in result.stdout


def test_config_get_nonexistent_key(tmp_path, monkeypatch, mock_questionary_init):
    """Test getting a nonexistent config key"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Try to get nonexistent key
    result = runner.invoke(app, ["config", "get", "nonexistent.key"])
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_config_set_new_key(tmp_path, monkeypatch, mock_questionary_init):
    """Test setting a new config key"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Set a new value
    result = runner.invoke(
        app, ["config", "set", "providers.text.openai.model", "gpt-4o"]
    )
    assert result.exit_code == 0
    assert "Configuration updated" in result.stdout

    # Verify it was set
    config_path = Path(".questfoundry") / "config.yml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    assert config["providers"]["text"]["openai"]["model"] == "gpt-4o"


def test_config_set_boolean_value(tmp_path, monkeypatch, mock_questionary_init):
    """Test setting a boolean config value"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Set a boolean value
    result = runner.invoke(
        app, ["config", "set", "ui.color", "false"]
    )
    assert result.exit_code == 0

    # Verify it was set as boolean
    config_path = Path(".questfoundry") / "config.yml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    assert config["ui"]["color"] is False


def test_config_masks_sensitive_values(tmp_path, monkeypatch, mock_questionary_init):
    """Test that sensitive values are masked"""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # Set an API key
    result = runner.invoke(
        app, ["config", "set", "providers.text.openai.api_key", "sk-1234567890abcdef"]
    )
    assert result.exit_code == 0

    # List config and verify masking
    result = runner.invoke(app, ["config", "list"])
    assert result.exit_code == 0
    assert "sk" in result.stdout  # Shows first 2 chars
    assert "********" in result.stdout  # Rest is masked
    assert "1234567890abcdef" not in result.stdout  # Full key not shown
