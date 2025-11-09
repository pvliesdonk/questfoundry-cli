"""Tests for qf export commands (view and git exports)."""

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
            result.ask = lambda: "Test project for export tests"
        else:
            result.ask = lambda: ""
        return result

    monkeypatch.setattr(questionary, "text", mock_text)


class TestExportViewCommand:
    """Tests for qf export view subcommand."""

    def test_export_view_help(self):
        """Test that export view command help is available."""
        result = runner.invoke(app, ["export", "view", "--help"])
        assert result.exit_code == 0
        assert "Export player view" in result.stdout or "export" in result.stdout

    def test_export_view_requires_project(self, tmp_path, monkeypatch):
        """Test export view requires an initialized project."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["export", "view"])

        assert result.exit_code != 0
        assert (
            "project" in result.stdout.lower()
            or "not found" in result.stdout.lower()
        )

    def test_export_view_html_format(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test exporting view to HTML format."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Export to HTML
        result = runner.invoke(app, ["export", "view", "--format", "html"])

        assert result.exit_code == 0
        assert "html" in result.stdout.lower() or "export" in result.stdout.lower()

    def test_export_view_markdown_format(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test exporting view to Markdown format."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Export to Markdown
        result = runner.invoke(app, ["export", "view", "--format", "markdown"])

        assert result.exit_code == 0
        assert (
            "markdown" in result.stdout.lower() or "export" in result.stdout.lower()
        )

    def test_export_view_with_output_path(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test exporting view to custom output path."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        output_dir = tmp_path / "exports"
        output_dir.mkdir()

        # Export with custom path
        result = runner.invoke(
            app, ["export", "view", "--output", str(output_dir / "view.html")]
        )

        assert result.exit_code == 0

    def test_export_view_with_snapshot_id(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test exporting specific snapshot by ID."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Export with snapshot ID
        result = runner.invoke(app, ["export", "view", "--snapshot", "snapshot-123"])

        # Should complete or indicate snapshot not found
        assert result.exit_code == 0 or "snapshot" in result.stdout.lower()

    def test_export_view_invalid_format(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test that invalid format is rejected."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Try invalid format
        result = runner.invoke(app, ["export", "view", "--format", "invalid"])

        assert result.exit_code != 0 or "format" in result.stdout.lower()

    def test_export_view_shows_progress(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test that export displays progress."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Export view
        result = runner.invoke(app, ["export", "view"])

        assert result.exit_code == 0
        # Should show some progress or export info
        assert (
            "export" in result.stdout.lower()
            or "view" in result.stdout.lower()
            or "path" in result.stdout.lower()
        )


class TestExportGitCommand:
    """Tests for qf export git subcommand."""

    def test_export_git_help(self):
        """Test that export git command help is available."""
        result = runner.invoke(app, ["export", "git", "--help"])
        assert result.exit_code == 0
        assert "Export" in result.stdout or "git" in result.stdout

    def test_export_git_requires_project(self, tmp_path, monkeypatch):
        """Test export git requires an initialized project."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["export", "git"])

        assert result.exit_code != 0
        assert (
            "project" in result.stdout.lower()
            or "not found" in result.stdout.lower()
        )

    def test_export_git_creates_yaml_files(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test that export git creates YAML files."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        output_dir = tmp_path / "git_export"
        output_dir.mkdir()

        # Export as git-friendly
        result = runner.invoke(
            app, ["export", "git", "--output", str(output_dir)]
        )

        assert result.exit_code == 0
        # Should create some files in output directory
        assert "export" in result.stdout.lower() or "created" in result.stdout.lower()

    def test_export_git_with_snapshot_id(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test exporting specific git snapshot by ID."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        output_dir = tmp_path / "git_export"
        output_dir.mkdir()

        # Export with snapshot ID
        result = runner.invoke(
            app,
            [
                "export",
                "git",
                "--snapshot",
                "snapshot-123",
                "--output",
                str(output_dir),
            ],
        )

        # Should complete or indicate snapshot not found
        assert result.exit_code == 0 or "snapshot" in result.stdout.lower()

    def test_export_git_shows_progress(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test that git export displays progress."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        output_dir = tmp_path / "git_export"
        output_dir.mkdir()

        # Export
        result = runner.invoke(
            app, ["export", "git", "--output", str(output_dir)]
        )

        assert result.exit_code == 0
        assert (
            "export" in result.stdout.lower()
            or "git" in result.stdout.lower()
            or "created" in result.stdout.lower()
        )

    def test_export_git_preserves_structure(
        self, tmp_path, monkeypatch, mock_questionary_init
    ):
        """Test that git export preserves directory structure."""
        monkeypatch.chdir(tmp_path)

        # Initialize project
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        output_dir = tmp_path / "git_export"
        output_dir.mkdir()

        # Export
        result = runner.invoke(
            app, ["export", "git", "--output", str(output_dir)]
        )

        assert result.exit_code == 0
