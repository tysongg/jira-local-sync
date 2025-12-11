"""Tests for configuration module."""

import pytest
from pydantic import ValidationError
from src.jira_local_sync.config import JiraSettings

pytestmark = pytest.mark.unit


def test_jira_settings_from_env(monkeypatch):
    """Test loading JiraSettings from environment variables."""
    monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "test-token-123")

    settings = JiraSettings()

    assert settings.jira_url == "https://test.atlassian.net"
    assert settings.jira_email == "test@example.com"
    assert settings.jira_api_token == "test-token-123"


def test_jira_settings_missing_required_fields(monkeypatch, tmp_path):
    """Test that JiraSettings raises error when required fields are missing."""
    # Clear any existing env vars
    monkeypatch.delenv("JIRA_URL", raising=False)
    monkeypatch.delenv("JIRA_EMAIL", raising=False)
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

    # Change to a temporary directory without .env file
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError) as exc_info:
        JiraSettings()

    # Should have errors for all three required fields
    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert "jira_url" in error_fields
    assert "jira_email" in error_fields
    assert "jira_api_token" in error_fields


def test_get_jira_auth(monkeypatch):
    """Test get_jira_auth returns correct authentication tuple."""
    monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "secret-token")

    settings = JiraSettings()
    auth = settings.get_jira_auth()

    assert auth == ("user@example.com", "secret-token")
    assert isinstance(auth, tuple)
    assert len(auth) == 2


def test_jira_settings_partial_env_vars(monkeypatch, tmp_path):
    """Test that partial environment variables still fail validation."""
    # Change to a temporary directory without .env file
    monkeypatch.chdir(tmp_path)

    # Clear and set specific env vars
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)
    monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    # Missing JIRA_API_TOKEN

    with pytest.raises(ValidationError) as exc_info:
        JiraSettings()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"][0] == "jira_api_token"
