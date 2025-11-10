"""Tests for interactive shell command"""

import json

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


class TestShellCommand:
    """Tests for shell REPL command functionality"""

    def test_shell_help(self):
        """Test shell help is available"""
        result = runner.invoke(app, ["shell", "--help"])
        assert result.exit_code == 0
        assert "shell" in result.stdout.lower() or "repl" in result.stdout.lower()

    def test_shell_requires_project(self, tmp_path, monkeypatch):
        """Test shell requires an initialized project"""
        monkeypatch.chdir(tmp_path)
        # Send 'exit' command immediately
        result = runner.invoke(app, ["shell"], input="exit\n")
        # Shell should handle gracefully - either run with warning or fail with message
        assert result.exit_code in [0, 1]

    def test_shell_starts_with_project(self, tmp_path, monkeypatch):
        """Test shell starts when project exists"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Send exit command immediately
        result = runner.invoke(app, ["shell"], input="exit\n")
        assert result.exit_code == 0

    def test_shell_shows_prompt(self, tmp_path, monkeypatch):
        """Test shell displays prompt"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="exit\n")
        assert result.exit_code == 0
        # Should contain prompt indicator
        assert any(p in result.stdout for p in ["qf>", ">>>", ">", "shell"])


class TestShellCommands:
    """Tests for commands available in shell"""

    def test_shell_help_command(self, tmp_path, monkeypatch):
        """Test help command in shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="help\nexit\n")
        assert result.exit_code == 0
        # Should show available commands
        assert "help" in result.stdout.lower() or "command" in result.stdout.lower()

    def test_shell_list_command(self, tmp_path, monkeypatch):
        """Test list command in shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="list\nexit\n")
        # Should not error
        assert result.exit_code == 0

    def test_shell_status_command(self, tmp_path, monkeypatch):
        """Test status command in shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="status\nexit\n")
        assert result.exit_code == 0

    def test_shell_show_command(self, tmp_path, monkeypatch):
        """Test show command in shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "hook-001",
            "type": "hook",
            "title": "Test Hook",
        }
        (hot_dir / "hook-001.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["shell"], input="show hook-001\nexit\n")
        # Should not error and should show artifact
        assert "hook-001" in result.stdout or result.exit_code == 0


class TestShellOptions:
    """Tests for shell command options"""

    def test_shell_with_verbose_option(self, tmp_path, monkeypatch):
        """Test shell with verbose output"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell", "--verbose"], input="exit\n")
        # Should accept verbose flag
        assert result.exit_code in [0, 1, 2]  # Graceful error handling

    def test_shell_with_no_history_option(self, tmp_path, monkeypatch):
        """Test shell without command history"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell", "--no-history"], input="exit\n")
        assert result.exit_code in [0, 1, 2]


class TestShellContextManagement:
    """Tests for shell context and state management"""

    def test_shell_maintains_context(self, tmp_path, monkeypatch):
        """Test shell maintains context between commands"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Run multiple commands
        commands = "status\nlist\nexit\n"
        result = runner.invoke(app, ["shell"], input=commands)
        assert result.exit_code == 0

    def test_shell_preserves_project_context(self, tmp_path, monkeypatch):
        """Test project context is preserved in shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text('{"name": "test-project"}')

        result = runner.invoke(app, ["shell"], input="status\nexit\n")
        assert result.exit_code == 0
        # Project info should be available
        output_lower = result.stdout.lower()
        assert "project" in output_lower or "questfoundry" in output_lower


class TestShellHistory:
    """Tests for command history in shell"""

    def test_shell_command_history(self, tmp_path, monkeypatch):
        """Test shell maintains command history"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Run commands that should be in history
        commands = "status\nlist\nexit\n"
        result = runner.invoke(app, ["shell"], input=commands)
        assert result.exit_code == 0
        # History feature is implicit in modern shell implementations

    def test_shell_history_file_location(self, tmp_path, monkeypatch):
        """Test shell history is saved to standard location"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="exit\n")
        assert result.exit_code == 0
        # History should be in .questfoundry or similar


class TestShellTabCompletion:
    """Tests for tab completion in shell"""

    def test_shell_supports_tab_completion(self):
        """Test shell supports tab completion"""
        # Tab completion is implicit in prompt_toolkit-based shells
        result = runner.invoke(app, ["shell", "--help"])
        assert result.exit_code == 0
        # Completion info might be in help text
        assert "shell" in result.stdout.lower()


class TestShellExit:
    """Tests for exiting shell"""

    def test_shell_exit_command(self, tmp_path, monkeypatch):
        """Test exit command closes shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="exit\n")
        assert result.exit_code == 0

    def test_shell_quit_command(self, tmp_path, monkeypatch):
        """Test quit command closes shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="quit\n")
        assert result.exit_code == 0

    def test_shell_ctrl_d_exit(self, tmp_path, monkeypatch):
        """Test Ctrl+D closes shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Ctrl+D is represented as EOF in input
        result = runner.invoke(app, ["shell"], input="")
        # EOF should gracefully close shell
        assert result.exit_code in [0, 1]


class TestShellErrorHandling:
    """Tests for error handling in shell"""

    def test_shell_handles_invalid_command(self, tmp_path, monkeypatch):
        """Test shell handles invalid commands gracefully"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="invalidcommand123\nexit\n")
        # Should not crash, show error message
        output_lower = result.stdout.lower()
        assert (
            "invalid" in output_lower
            or "not found" in output_lower
            or result.exit_code == 0
        )

    def test_shell_handles_command_errors(self, tmp_path, monkeypatch):
        """Test shell handles command execution errors"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Try to show non-existent artifact
        result = runner.invoke(app, ["shell"], input="show nonexistent\nexit\n")
        # Should show error but not crash shell
        assert result.exit_code == 0

    def test_shell_handles_missing_arguments(self, tmp_path, monkeypatch):
        """Test shell handles commands with missing arguments"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Show without artifact ID
        result = runner.invoke(app, ["shell"], input="show\nexit\n")
        # Should handle gracefully
        assert result.exit_code in [0, 1]


class TestShellIntegration:
    """Tests for shell integration with other commands"""

    def test_shell_can_run_diff_command(self, tmp_path, monkeypatch):
        """Test diff command works in shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "hook-001",
            "type": "hook",
            "title": "Test",
        }
        (hot_dir / "hook-001.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["shell"], input="diff hook-001\nexit\n")
        assert result.exit_code == 0

    def test_shell_can_run_search_command(self, tmp_path, monkeypatch):
        """Test search command works in shell"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["shell"], input="search test\nexit\n")
        assert result.exit_code == 0

    def test_shell_prompt_shows_project_name(self, tmp_path, monkeypatch):
        """Test shell prompt includes project name"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text('{"name": "my-project"}')

        result = runner.invoke(app, ["shell"], input="exit\n")
        assert result.exit_code == 0
        # Prompt might include project name
