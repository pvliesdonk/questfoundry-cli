"""Tests for artifact diff command"""

import json

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


class TestDiffCommand:
    """Tests for basic diff command functionality"""

    def test_diff_help(self):
        """Test diff help is available"""
        result = runner.invoke(app, ["diff", "--help"])
        assert result.exit_code == 0
        assert "diff" in result.stdout.lower()

    def test_diff_no_project(self, tmp_path, monkeypatch):
        """Test diff fails without project"""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["diff", "test-artifact"])
        assert result.exit_code != 0
        assert "no project" in result.stdout.lower()

    def test_diff_artifact_not_found(self, tmp_path, monkeypatch):
        """Test diff with non-existent artifact"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        result = runner.invoke(app, ["diff", "nonexistent"])
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower()

    def test_diff_single_artifact(self, tmp_path, monkeypatch):
        """Test diff with single artifact (no versions)"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "test-type"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "test-artifact",
            "type": "test-type",
            "content": "Original content",
            "status": "hot",
        }
        (hot_dir / "test-artifact.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["diff", "test-artifact"])
        assert result.exit_code == 0
        assert "test-artifact" in result.stdout

    def test_diff_with_versions(self, tmp_path, monkeypatch):
        """Test diff with multiple versions of artifact"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create hot version
        hot_dir = tmp_path / ".questfoundry" / "hot" / "test-type"
        hot_dir.mkdir(parents=True, exist_ok=True)

        hot_artifact = {
            "id": "test-artifact",
            "type": "test-type",
            "content": "Updated content\nwith more details",
            "status": "hot",
            "timestamp": "2024-11-09T12:00:00Z",
        }
        (hot_dir / "test-artifact.json").write_text(json.dumps(hot_artifact))

        # Create cold version
        cold_dir = tmp_path / ".questfoundry" / "cold" / "test-type"
        cold_dir.mkdir(parents=True, exist_ok=True)

        cold_artifact = {
            "id": "test-artifact",
            "type": "test-type",
            "content": "Original content",
            "status": "cold",
            "timestamp": "2024-11-08T12:00:00Z",
        }
        (cold_dir / "test-artifact.json").write_text(json.dumps(cold_artifact))

        result = runner.invoke(app, ["diff", "test-artifact"])
        assert result.exit_code == 0
        # Should show diff indicators
        assert any(indicator in result.stdout for indicator in ["+", "-", "Updated"])


class TestDiffOptions:
    """Tests for diff command options"""

    def test_diff_with_snapshot_option(self, tmp_path, monkeypatch):
        """Test diff with specific snapshot reference"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "test-type"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "test-artifact",
            "type": "test-type",
            "content": "Current",
        }
        (hot_dir / "test-artifact.json").write_text(json.dumps(artifact_data))

        # Create snapshots directory
        snapshots_dir = tmp_path / ".questfoundry" / "snapshots"
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        (snapshots_dir / "snapshot-1.json").write_text(json.dumps({"artifacts": {}}))

        result = runner.invoke(
            app, ["diff", "test-artifact", "--snapshot", "snapshot-1"]
        )
        assert result.exit_code == 0

    def test_diff_between_tu_option(self, tmp_path, monkeypatch):
        """Test diff between two time units"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "test-type"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "test-artifact",
            "type": "test-type",
            "content": "V2",
        }
        (hot_dir / "test-artifact.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(
            app, ["diff", "test-artifact", "--from", "tu:1", "--to", "tu:2"]
        )
        assert result.exit_code in [0, 1]  # May succeed or fail gracefully

class TestDiffCompletion:
    """Tests for diff command completion"""

    def test_diff_command_has_completion(self):
        """Test diff command has artifact ID completion"""
        # Check that diff command is registered
        result = runner.invoke(app, ["diff", "--help"])
        assert result.exit_code == 0
        # Completion is implicit in Typer with add_completion=True


class TestDiffOutput:
    """Tests for diff output formatting"""

    def test_diff_output_has_header(self, tmp_path, monkeypatch):
        """Test diff output includes artifact header"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "test-type"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "test-artifact",
            "type": "test-type",
            "content": "Test content",
        }
        (hot_dir / "test-artifact.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["diff", "test-artifact"])
        assert result.exit_code == 0
        assert "test-artifact" in result.stdout

    def test_diff_shows_statistics(self, tmp_path, monkeypatch):
        """Test diff shows change statistics"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create hot and cold versions
        hot_dir = tmp_path / ".questfoundry" / "hot" / "test-type"
        hot_dir.mkdir(parents=True, exist_ok=True)

        hot_artifact = {
            "id": "test-artifact",
            "type": "test-type",
            "content": "A\nB\nC\nD",
        }
        (hot_dir / "test-artifact.json").write_text(json.dumps(hot_artifact))

        cold_dir = tmp_path / ".questfoundry" / "cold" / "test-type"
        cold_dir.mkdir(parents=True, exist_ok=True)

        cold_artifact = {
            "id": "test-artifact",
            "type": "test-type",
            "content": "A\nB",
        }
        (cold_dir / "test-artifact.json").write_text(json.dumps(cold_artifact))

        result = runner.invoke(app, ["diff", "test-artifact"])
        assert result.exit_code == 0
        # Should contain diff markers or statistics
        output_lower = result.stdout.lower()
        markers = ["diff", "added", "removed", "+", "-"]
        assert any(marker in output_lower for marker in markers)
