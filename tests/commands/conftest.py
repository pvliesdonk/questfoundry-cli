"""Shared test fixtures"""

import pytest
import questionary


@pytest.fixture
def mock_questionary_init(monkeypatch):
    """Mock questionary.text for project initialization"""
    original_text = questionary.text

    def mock_text(message, **kwargs):
        result = original_text(message, **kwargs)
        if "name" in message.lower():
            result.ask = lambda: "test-project"
        elif "description" in message.lower():
            result.ask = lambda: "Test description"
        return result

    monkeypatch.setattr(questionary, "text", mock_text)
