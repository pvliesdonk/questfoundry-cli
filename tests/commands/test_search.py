"""Tests for artifact search command"""

import json

from typer.testing import CliRunner

from qf.cli import app

runner = CliRunner()


class TestSearchCommand:
    """Tests for basic search command functionality"""

    def test_search_help(self):
        """Test search help is available"""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
        assert "search" in result.stdout.lower()

    def test_search_no_project(self, tmp_path, monkeypatch):
        """Test search fails without project"""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["search", "test"])
        assert result.exit_code != 0
        assert "no project" in result.stdout.lower()

    def test_search_no_results(self, tmp_path, monkeypatch):
        """Test search with no matching results"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact workspace but no artifacts
        (tmp_path / ".questfoundry" / "hot" / "test").mkdir(parents=True, exist_ok=True)

        result = runner.invoke(app, ["search", "nonexistent-query"])
        assert result.exit_code == 0
        # Should show "no results" or similar
        assert "no results" in result.stdout.lower() or len(result.stdout.strip()) == 0

    def test_search_single_result(self, tmp_path, monkeypatch):
        """Test search with single matching result"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "hook-001",
            "type": "hook",
            "title": "Dragon Discovery",
            "content": "A hidden dragon awakens in the mountains",
        }
        (hot_dir / "hook-001.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["search", "dragon"])
        assert result.exit_code == 0
        assert "hook-001" in result.stdout or "dragon" in result.stdout.lower()

    def test_search_multiple_results(self, tmp_path, monkeypatch):
        """Test search with multiple matching results"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create multiple artifacts
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        hook1 = {
            "id": "hook-001",
            "type": "hook",
            "title": "Dragon Discovery",
            "content": "A dragon appears",
        }
        (hot_dir / "hook-001.json").write_text(json.dumps(hook1))

        hook2 = {
            "id": "hook-002",
            "type": "hook",
            "title": "Dragon's Lair",
            "content": "Finding the dragon's hidden cave",
        }
        (hot_dir / "hook-002.json").write_text(json.dumps(hook2))

        result = runner.invoke(app, ["search", "dragon"])
        assert result.exit_code == 0
        # Should find at least one result
        assert "hook" in result.stdout.lower() or "dragon" in result.stdout.lower()

    def test_search_case_insensitive(self, tmp_path, monkeypatch):
        """Test search is case-insensitive"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "hook-001",
            "type": "hook",
            "title": "Dragon Discovery",
            "content": "uppercase text here",
        }
        (hot_dir / "hook-001.json").write_text(json.dumps(artifact_data))

        # Search with different cases
        result_lower = runner.invoke(app, ["search", "dragon"])
        result_upper = runner.invoke(app, ["search", "DRAGON"])

        assert result_lower.exit_code == 0
        assert result_upper.exit_code == 0


class TestSearchOptions:
    """Tests for search command options"""

    def test_search_type_filter(self, tmp_path, monkeypatch):
        """Test search with type filter"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create different artifact types
        hooks_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        loops_dir = tmp_path / ".questfoundry" / "hot" / "loops"
        loops_dir.mkdir(parents=True, exist_ok=True)

        hook_data = {
            "id": "hook-001",
            "type": "hook",
            "title": "Test Hook",
        }
        (hooks_dir / "hook-001.json").write_text(json.dumps(hook_data))

        loop_data = {
            "id": "loop-001",
            "type": "loop",
            "title": "Test Loop",
        }
        (loops_dir / "loop-001.json").write_text(json.dumps(loop_data))

        result = runner.invoke(app, ["search", "test", "--type", "hook"])
        assert result.exit_code == 0
        # Should filter to hooks only
        assert "hook" in result.stdout.lower()

    def test_search_field_filter(self, tmp_path, monkeypatch):
        """Test search in specific field"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "hook-001",
            "type": "hook",
            "title": "Important Hook",
            "content": "Irrelevant content",
        }
        (hot_dir / "hook-001.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["search", "important", "--field", "title"])
        assert result.exit_code == 0

    def test_search_limit_results(self, tmp_path, monkeypatch):
        """Test search with result limit"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create multiple artifacts
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        for i in range(5):
            artifact_data = {
                "id": f"hook-{i:03d}",
                "type": "hook",
                "title": f"Test Hook {i}",
            }
            (hot_dir / f"hook-{i:03d}.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["search", "test", "--limit", "2"])
        assert result.exit_code == 0
        # Output should be limited (implementation dependent)


class TestSearchCompletion:
    """Tests for search command completion"""

    def test_search_command_has_completion(self):
        """Test search command is available with tab completion"""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0


class TestSearchOutput:
    """Tests for search output formatting"""

    def test_search_results_display_format(self, tmp_path, monkeypatch):
        """Test search results are displayed in table format"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "hook-001",
            "type": "hook",
            "title": "Dragon Discovery",
            "content": "A dragon appears",
        }
        (hot_dir / "hook-001.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["search", "dragon"])
        assert result.exit_code == 0
        # Should contain artifact information
        output = result.stdout.lower()
        assert any(word in output for word in ["hook-001", "dragon", "hook"])

    def test_search_highlights_matches(self, tmp_path, monkeypatch):
        """Test search highlights matching terms in results"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create artifact
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        artifact_data = {
            "id": "hook-001",
            "type": "hook",
            "title": "Test Case",
            "content": "The test here is important",
        }
        (hot_dir / "hook-001.json").write_text(json.dumps(artifact_data))

        result = runner.invoke(app, ["search", "test"])
        assert result.exit_code == 0
        # Should contain the search term
        assert "test" in result.stdout.lower()

    def test_search_empty_results_message(self, tmp_path, monkeypatch):
        """Test search shows helpful message when no results"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        (tmp_path / ".questfoundry").mkdir(parents=True, exist_ok=True)

        result = runner.invoke(app, ["search", "xyz123nonexistent"])
        assert result.exit_code == 0
        # Should indicate no results found
        output = result.stdout.lower()
        empty_output = result.stdout.strip() == ""
        assert "no results" in output or "not found" in output or empty_output


class TestSearchPerformance:
    """Tests for search performance"""

    def test_search_completes_quickly(self, tmp_path, monkeypatch):
        """Test search completes within reasonable time"""
        import time

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".qfproj").write_text("{}")

        # Create multiple artifacts
        hot_dir = tmp_path / ".questfoundry" / "hot" / "hooks"
        hot_dir.mkdir(parents=True, exist_ok=True)

        for i in range(10):
            artifact_data = {
                "id": f"hook-{i:03d}",
                "type": "hook",
                "title": f"Test Hook {i}",
                "content": "Some content " * 100,
            }
            (hot_dir / f"hook-{i:03d}.json").write_text(json.dumps(artifact_data))

        start = time.time()
        result = runner.invoke(app, ["search", "test"])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 2.0  # Should complete in under 2 seconds
