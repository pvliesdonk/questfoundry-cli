"""Tests for run command"""


from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


def test_run_without_project(tmp_path, monkeypatch):
    """Test running a loop without a project"""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["run", "run", "hook-harvest"])

    assert result.exit_code == 1
    assert "No project found" in result.stdout


def test_run_with_valid_loop(tmp_path, monkeypatch, mock_questionary_init):
    """Test running a valid loop in a project"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # run a loop
    result = runner.invoke(app, ["run", "run", "hook-harvest"])

    assert result.exit_code == 0
    assert "Hook Harvest" in result.stdout
    assert "HH" in result.stdout
    assert "Summary" in result.stdout


def test_run_with_invalid_loop(tmp_path, monkeypatch, mock_questionary_init):
    """Test running an invalid loop name"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # try invalid loop
    result = runner.invoke(app, ["run", "run", "invalid-loop"])

    assert result.exit_code == 1
    assert "Unknown loop" in result.stdout
    assert "Available loops" in result.stdout


def test_run_with_display_name(tmp_path, monkeypatch, mock_questionary_init):
    """Test running a loop using display name"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # run using display name
    result = runner.invoke(app, ["run", "run", "Story Spark"])

    assert result.exit_code == 0
    assert "Story Spark" in result.stdout
    assert "SS" in result.stdout


def test_run_shows_progress(tmp_path, monkeypatch, mock_questionary_init):
    """Test that running shows progress indicators"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # run loop
    result = runner.invoke(app, ["run", "run", "lore-deepening"])

    assert result.exit_code == 0
    # check for activity indicators
    assert "→" in result.stdout or "✓" in result.stdout
    assert "Initializing" in result.stdout


def test_run_shows_summary(tmp_path, monkeypatch, mock_questionary_init):
    """Test that running shows execution summary"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # run loop
    result = runner.invoke(app, ["run", "run", "codex-expansion"])

    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "Codex Expansion" in result.stdout
    assert "Activities" in result.stdout


def test_run_suggests_next_action(tmp_path, monkeypatch, mock_questionary_init):
    """Test that running suggests next action"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # run hook-harvest (should suggest lore-deepening next)
    result = runner.invoke(app, ["run", "run", "hook-harvest"])

    assert result.exit_code == 0
    assert "Next Action" in result.stdout or "next" in result.stdout.lower()


def test_run_interactive_flag(tmp_path, monkeypatch, mock_questionary_init):
    """Test interactive flag shows future message"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # run with interactive flag
    result = runner.invoke(app, ["run", "run", "story-spark", "--interactive"])

    assert result.exit_code == 0
    assert "Interactive mode" in result.stdout or "future" in result.stdout


def test_run_all_discovery_loops(tmp_path, monkeypatch, mock_questionary_init):
    """Test all discovery category loops execute"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    discovery_loops = ["story-spark", "hook-harvest", "lore-deepening"]

    for loop in discovery_loops:
        result = runner.invoke(app, ["run", "run", loop])
        assert result.exit_code == 0
        assert "Summary" in result.stdout


def test_run_all_refinement_loops(tmp_path, monkeypatch, mock_questionary_init):
    """Test all refinement category loops execute"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    refinement_loops = ["codex-expansion", "style-tuneup"]

    for loop in refinement_loops:
        result = runner.invoke(app, ["run", "run", loop])
        assert result.exit_code == 0
        assert "Summary" in result.stdout


def test_run_all_asset_loops(tmp_path, monkeypatch, mock_questionary_init):
    """Test all asset category loops execute"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    asset_loops = ["art-touchup", "audio-pass", "translation-pass"]

    for loop in asset_loops:
        result = runner.invoke(app, ["run", "run", loop])
        assert result.exit_code == 0
        assert "Summary" in result.stdout


def test_run_all_export_loops(tmp_path, monkeypatch, mock_questionary_init):
    """Test all export category loops execute"""
    monkeypatch.chdir(tmp_path)

    # initialize project
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    export_loops = [
        "binding-run",
        "narration-dry-run",
        "gatecheck",
        "post-mortem",
        "archive-snapshot",
    ]

    for loop in export_loops:
        result = runner.invoke(app, ["run", "run", loop])
        assert result.exit_code == 0
        assert "Summary" in result.stdout


def test_run_help(tmp_path):
    """Test run command help text"""
    result = runner.invoke(app, ["run", "run", "--help"])

    assert result.exit_code == 0
    assert "Execute a loop" in result.stdout
    assert "LOOP_NAME" in result.stdout or "loop" in result.stdout.lower()
    assert "--interactive" in result.stdout
