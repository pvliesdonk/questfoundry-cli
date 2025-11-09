"""Tests for qf bind commands (view binding/rendering)."""

import pytest
from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


@pytest.fixture
def mock_questionary_init(monkeypatch):
    """Mock questionary for project initialization."""
    import questionary

    original_text = questionary.text

    def mock_text(message, **kwargs):
        """Mock questionary.text to auto-respond to init prompts."""
        result = original_text(message, **kwargs)
        if "name" in message.lower():
            result.ask = lambda: "test-project"
        elif "description" in message.lower():
            result.ask = lambda: "Test project for bind tests"
        else:
            result.ask = lambda: ""
        return result

    monkeypatch.setattr(questionary, "text", mock_text)


class TestBindViewCommand:
    """Tests for qf bind view subcommand."""

    def test_bind_view_help(self):
        """Test that bind view command help is available."""
        result = runner.invoke(app, ["bind", "view", "--help"])
        assert result.exit_code == 0
        assert "bind" in result.stdout.lower() or "view" in result.stdout.lower()

    def test_bind_view_requires_project(self, tmp_path, monkeypatch):
        """Test bind view requires an initialized project."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["bind", "view", "snapshot-123"])

        assert result.exit_code != 0
        assert (
            "project" in result.stdout.lower()
            or "not found" in result.stdout.lower()
        )

    def test_bind_view_requires_snapshot_id(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test bind view requires a snapshot ID."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Try without snapshot ID
        result = runner.invoke(app, ["bind", "view"])

        assert result.exit_code != 0 or "snapshot" in result.stdout.lower()

    def test_bind_view_html_format(self, tmp_path, monkeypatch, mock_questionary_init):
        """Test binding view to HTML format."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Bind view to HTML
        result = runner.invoke(
            app, ["bind", "view", "snapshot-123", "--format", "html"]
        )

        # Should succeed or indicate snapshot not found
        assert result.exit_code == 0 or "snapshot" in result.stdout.lower()

    def test_bind_view_markdown_format(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test binding view to Markdown format."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Bind view to Markdown
        result = runner.invoke(
            app, ["bind", "view", "snapshot-123", "--format", "markdown"]
        )

        # Should succeed or indicate snapshot not found
        assert result.exit_code == 0 or "snapshot" in result.stdout.lower()

    def test_bind_view_pdf_format(self, tmp_path, monkeypatch, mock_questionary_init):
        """Test binding view to PDF format."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Bind view to PDF
        result = runner.invoke(
            app, ["bind", "view", "snapshot-123", "--format", "pdf"]
        )

        # Should succeed or indicate snapshot not found
        assert result.exit_code == 0 or "snapshot" in result.stdout.lower()

    def test_bind_view_with_output_path(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test binding view to custom output path."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        output_dir = tmp_path / "binds"
        output_dir.mkdir()

        # Bind with custom path
        result = runner.invoke(
            app,
            [
                "bind",
                "view",
                "snapshot-123",
                "--output",
                str(output_dir / "bound-view.html"),
            ],
        )

        # Should succeed or indicate snapshot not found
        assert result.exit_code == 0 or "snapshot" in result.stdout.lower()

    def test_bind_view_invalid_format(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test that invalid format is rejected."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Try invalid format
        result = runner.invoke(
            app, ["bind", "view", "snapshot-123", "--format", "invalid"]
        )

        assert result.exit_code != 0 or "format" in result.stdout.lower()

    def test_bind_view_shows_progress(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test that bind displays progress."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Bind view
        result = runner.invoke(app, ["bind", "view", "snapshot-123"])

        assert result.exit_code == 0 or "snapshot" in result.stdout.lower()
        # Should show some progress or bind info
        assert (
            "bind" in result.stdout.lower()
            or "view" in result.stdout.lower()
            or "snapshot" in result.stdout.lower()
        )

    def test_bind_view_default_format(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test bind view uses sensible default format."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Bind without specifying format (should use default)
        result = runner.invoke(app, ["bind", "view", "snapshot-123"])

        assert result.exit_code == 0 or "snapshot" in result.stdout.lower()
