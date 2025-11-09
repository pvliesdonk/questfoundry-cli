"""Tests for quickstart workflow command."""

import contextlib
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from qf.cli import app
from qf.interactive import QuickstartSession

runner = CliRunner(mix_stderr=False)


@pytest.fixture
def mock_prompts() -> dict:
    """Fixture providing mocked questionary prompts for TTY-less testing."""
    return {
        "ask_premise": MagicMock(return_value="A mysterious tale unfolds"),
        "ask_tone": MagicMock(return_value="Mystery"),
        "ask_length": MagicMock(return_value="Novella (20-50 pages)"),
        "ask_project_name": MagicMock(return_value="test-project"),
        "confirm_setup": MagicMock(return_value=True),
        "ask_review_artifacts": MagicMock(return_value=False),
        "ask_continue_loop": MagicMock(return_value=False),
        "ask_agent_response": MagicMock(return_value="Test response"),
    }


@pytest.fixture
def mock_is_interactive() -> None:
    """Fixture that mocks _is_interactive to return True for testing."""
    with patch("qf.interactive.prompts._is_interactive", return_value=True):
        yield


class TestQuickstartSession:
    """Tests for QuickstartSession class."""

    def test_session_initialization(self) -> None:
        """Test session initializes with default values."""
        session = QuickstartSession()

        assert session.project_name == ""
        assert session.project_file is None
        assert session.workspace_dir is None
        assert session.completed_loops == []
        assert session.current_loop is None
        assert session.interactive_mode is False

    def test_create_project_success(self) -> None:
        """Test successful project creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                session = QuickstartSession()
                success = session.create_project(
                    "test-project",
                    "A test story premise",
                    "Mystery",
                    "Novella",
                )

                assert success is True
                assert session.project_name == "test-project"
                assert session.workspace_dir is not None
                assert session.workspace_dir.exists()

                # Check workspace subdirectories exist
                assert (session.workspace_dir / "hot").exists()
                assert (session.workspace_dir / "cold").exists()
                assert (session.workspace_dir / "assets").exists()

                # Check metadata file created
                metadata_file = session.workspace_dir / "project.json"
                assert metadata_file.exists()

                metadata = json.loads(metadata_file.read_text())
                assert metadata["name"] == "test-project"
                assert metadata["premise"] == "A test story premise"

            finally:
                os.chdir(old_cwd)

    def test_start_loop(self) -> None:
        """Test marking loop as started."""
        session = QuickstartSession()
        session.start_loop("hook-harvest")

        assert session.current_loop == "hook-harvest"

    def test_complete_loop(self) -> None:
        """Test marking loop as completed."""
        session = QuickstartSession()
        session.start_loop("hook-harvest")
        session.complete_loop("hook-harvest")

        assert session.current_loop is None
        assert "hook-harvest" in session.completed_loops

    def test_complete_loop_idempotent(self) -> None:
        """Test that completing a loop multiple times is safe."""
        session = QuickstartSession()
        session.complete_loop("hook-harvest")
        session.complete_loop("hook-harvest")

        assert session.completed_loops.count("hook-harvest") == 1

    def test_save_checkpoint(self) -> None:
        """Test saving checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                session = QuickstartSession()
                session.create_project(
                    "test-project",
                    "A test premise",
                    "Horror",
                    "Novel",
                )
                session.complete_loop("hook-harvest")
                session.save_checkpoint()

                checkpoint_file = Path(".questfoundry") / ".quickstart_checkpoint.json"
                assert checkpoint_file.exists()

                checkpoint = json.loads(checkpoint_file.read_text())
                assert checkpoint["project_name"] == "test-project"
                assert "hook-harvest" in checkpoint["completed_loops"]

            finally:
                os.chdir(old_cwd)

    def test_load_checkpoint(self) -> None:
        """Test loading checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Create and save checkpoint
                session1 = QuickstartSession()
                session1.create_project(
                    "test-project",
                    "A test premise",
                    "Adventure",
                    "Short",
                )
                session1.complete_loop("hook-harvest")
                session1.enable_interactive_mode()
                session1.save_checkpoint()

                # Load checkpoint in new session
                session2 = QuickstartSession()
                success = session2.load_checkpoint()

                assert success is True
                assert session2.project_name == "test-project"
                assert "hook-harvest" in session2.completed_loops
                assert session2.interactive_mode is True

            finally:
                os.chdir(old_cwd)

    def test_can_resume(self) -> None:
        """Test checking if session can resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Initially cannot resume
                session = QuickstartSession()
                assert session.can_resume() is False

                # After creating project and checkpoint, can resume
                session.create_project(
                    "test-project",
                    "A test premise",
                    "Mystery",
                    "Novella",
                )
                session.save_checkpoint()

                assert session.can_resume() is True

            finally:
                os.chdir(old_cwd)

    def test_get_session_status(self) -> None:
        """Test getting session status."""
        session = QuickstartSession()
        session.project_name = "test-project"
        session.premise = "A test premise"
        session.tone = "Mystery"
        session.length = "Novella"
        session.complete_loop("hook-harvest")
        session.enable_interactive_mode()

        status = session.get_session_status()

        assert status["project_name"] == "test-project"
        assert status["premise"] == "A test premise"
        assert status["tone"] == "Mystery"
        assert status["length"] == "Novella"
        assert "hook-harvest" in status["completed_loops"]
        assert status["interactive_mode"] is True
        assert "elapsed_time" in status

    def test_enable_interactive_mode(self) -> None:
        """Test enabling interactive mode."""
        session = QuickstartSession()
        assert session.interactive_mode is False

        session.enable_interactive_mode()
        assert session.interactive_mode is True

    def test_disable_interactive_mode(self) -> None:
        """Test disabling interactive mode."""
        session = QuickstartSession()
        session.enable_interactive_mode()
        assert session.interactive_mode is True

        session.disable_interactive_mode()
        assert session.interactive_mode is False


class TestQuickstartCommand:
    """Tests for quickstart command."""

    def test_quickstart_without_project(self) -> None:
        """Test quickstart in directory with no existing project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                result = runner.invoke(
                    app, ["quickstart", "--help"], env={"COLUMNS": "200"}
                )
                assert result.exit_code == 0
                assert "guided" in result.stdout.lower()
                assert "interactive" in result.stdout.lower()

            finally:
                os.chdir(old_cwd)

    def test_quickstart_help(self) -> None:
        """Test quickstart help text."""
        result = runner.invoke(
            app, ["quickstart", "--help"], env={"COLUMNS": "200"}
        )

        assert result.exit_code == 0
        assert "quickstart" in result.stdout.lower()
        assert "guided" in result.stdout.lower()
        assert "interactive" in result.stdout.lower()
        assert "resume" in result.stdout.lower()

    def test_quickstart_guided_flag(self) -> None:
        """Test that --guided flag is recognized."""
        result = runner.invoke(
            app, ["quickstart", "--help"], env={"COLUMNS": "200"}
        )
        assert "--guided" in result.stdout

    def test_quickstart_interactive_flag(self) -> None:
        """Test that --interactive flag is recognized."""
        result = runner.invoke(
            app, ["quickstart", "--help"], env={"COLUMNS": "200"}
        )
        assert "--interactive" in result.stdout or "-i" in result.stdout

    def test_quickstart_resume_flag(self) -> None:
        """Test that --resume flag is recognized."""
        result = runner.invoke(
            app, ["quickstart", "--help"], env={"COLUMNS": "200"}
        )
        assert "--resume" in result.stdout


class TestQuickstartIntegration:
    """Integration tests for quickstart workflow."""

    def test_project_creation_workflow(self) -> None:
        """Test basic project creation workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                session = QuickstartSession()
                success = session.create_project(
                    "integration-test",
                    "An integration test premise",
                    "Fantasy",
                    "Novel",
                )

                assert success is True
                assert session.workspace_dir is not None
                assert (session.workspace_dir / "project.json").exists()

            finally:
                os.chdir(old_cwd)

    def test_loop_execution_sequence(self) -> None:
        """Test loop execution sequence."""
        session = QuickstartSession()
        loops = ["Hook Harvest", "Lore Deepening", "Story Spark"]

        for loop in loops:
            session.start_loop(loop)
            assert session.current_loop == loop
            session.complete_loop(loop)

        assert session.completed_loops == loops
        assert session.current_loop is None

    def test_checkpoint_resume_workflow(self) -> None:
        """Test checkpoint save and resume workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Initial session - create project and execute loops
                session1 = QuickstartSession()
                session1.create_project(
                    "checkpoint-test",
                    "Test premise",
                    "Mystery",
                    "Novella",
                )
                session1.complete_loop("Hook Harvest")
                session1.complete_loop("Lore Deepening")
                session1.save_checkpoint()

                # Resume session - load checkpoint and continue
                session2 = QuickstartSession()
                assert session2.load_checkpoint() is True
                assert session2.project_name == "checkpoint-test"
                assert len(session2.completed_loops) == 2

                # Continue with more loops
                session2.complete_loop("Story Spark")
                assert len(session2.completed_loops) == 3

            finally:
                os.chdir(old_cwd)

    def test_interactive_mode_workflow(self) -> None:
        """Test interactive mode enablement."""
        session = QuickstartSession()
        assert session.interactive_mode is False

        session.enable_interactive_mode()
        assert session.interactive_mode is True

        status = session.get_session_status()
        assert status["interactive_mode"] is True


class TestQuickstartInteractive:
    """Tests for quickstart command with TTY emulation."""

    def test_quickstart_command_with_tty(
        self, mock_is_interactive: None, mock_prompts: dict
    ) -> None:
        """Test quickstart command when TTY is available (mocked)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Apply all patches at once using ExitStack
                with contextlib.ExitStack() as stack:
                    stack.enter_context(
                        patch(
                            "qf.commands.quickstart.ask_premise",
                            return_value="A test story premise",
                        )
                    )
                    stack.enter_context(
                        patch(
                            "qf.commands.quickstart.ask_tone", return_value="Mystery"
                        )
                    )
                    stack.enter_context(
                        patch(
                            "qf.commands.quickstart.ask_length",
                            return_value="Novella (20-50 pages)",
                        )
                    )
                    stack.enter_context(
                        patch(
                            "qf.commands.quickstart.ask_project_name",
                            return_value="test-project",
                        )
                    )
                    stack.enter_context(
                        patch(
                            "qf.commands.quickstart.confirm_setup", return_value=True
                        )
                    )
                    stack.enter_context(
                        patch(
                            "qf.commands.quickstart.ask_review_artifacts",
                            return_value=False,
                        )
                    )
                    # User continues through all loops
                    stack.enter_context(
                        patch(
                            "qf.commands.quickstart.ask_continue_loop",
                            return_value=True,
                        )
                    )

                    result = runner.invoke(
                        app,
                        ["quickstart"],
                        env={"TERM": "xterm-256color", "COLUMNS": "120"},
                    )

                # Command should complete successfully
                assert result.exit_code == 0
                assert "Quickstart Complete" in result.stdout

                # Project files should be created
                assert Path(".questfoundry").exists()
                assert (Path(".questfoundry") / "project.json").exists()

            finally:
                os.chdir(old_cwd)

    def test_quickstart_command_without_tty(self) -> None:
        """Test quickstart command fails gracefully without TTY (no mock)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Don't mock _is_interactive, so it returns False
                result = runner.invoke(app, ["quickstart"])

                # Should fail with clear error message
                assert result.exit_code == 1
                # Check both stdout for the error message
                assert (
                    "Interactive mode requires a TTY" in result.stdout
                    or "Interactive mode requires a TTY" in str(result.exception)
                )

            finally:
                os.chdir(old_cwd)

    def test_quickstart_resume_with_checkpoint(self, mock_is_interactive: None) -> None:
        """Test quickstart resume flag with checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # First create a project and checkpoint
                session = QuickstartSession()
                session.create_project(
                    "resume-test",
                    "Test premise",
                    "Fantasy",
                    "Novel",
                )
                session.complete_loop("Hook Harvest")
                session.save_checkpoint()

                # Now test resume with mocked prompts
                with patch(
                    "qf.commands.quickstart.ask_review_artifacts",
                    return_value=False,
                ):
                    with patch(
                        "qf.commands.quickstart.ask_continue_loop",
                        return_value=False,
                    ):
                        result = runner.invoke(
                            app,
                            ["quickstart", "--resume"],
                            env={"TERM": "xterm-256color", "COLUMNS": "120"},
                        )

                assert result.exit_code == 0
                assert "Resumed from checkpoint" in result.stdout

            finally:
                os.chdir(old_cwd)
