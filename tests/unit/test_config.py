"""Tests for configuration module."""

import pytest
from pydantic import ValidationError
from src.jira_local_sync.config import JiraSettings

pytestmark = pytest.mark.unit


def test_jira_settings_from_kwargs():
    """Test creating JiraSettings from keyword arguments."""
    settings = JiraSettings(
        jira_url="https://test.atlassian.net",
        jira_email="test@example.com",
        jira_api_token="test-token-123"
    )

    assert settings.jira_url == "https://test.atlassian.net"
    assert settings.jira_email == "test@example.com"
    assert settings.jira_api_token == "test-token-123"


def test_jira_settings_from_dict():
    """Test creating JiraSettings from dictionary."""
    config_dict = {
        "jira_url": "https://test.atlassian.net",
        "jira_email": "test@example.com",
        "jira_api_token": "test-token-123"
    }
    settings = JiraSettings(**config_dict)

    assert settings.jira_url == "https://test.atlassian.net"
    assert settings.jira_email == "test@example.com"
    assert settings.jira_api_token == "test-token-123"


def test_jira_settings_missing_required_fields():
    """Test that JiraSettings raises error when required fields are missing."""
    with pytest.raises(ValidationError) as exc_info:
        JiraSettings(
            jira_url="https://test.atlassian.net",
            jira_email="test@example.com"
            # Missing jira_api_token
        )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"][0] == "jira_api_token"


def test_jira_settings_all_fields_missing():
    """Test that JiraSettings raises error when all fields are missing."""
    with pytest.raises(ValidationError) as exc_info:
        JiraSettings()

    # Should have errors for all three required fields
    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert "jira_url" in error_fields
    assert "jira_email" in error_fields
    assert "jira_api_token" in error_fields


def test_get_jira_auth():
    """Test get_jira_auth returns correct authentication tuple."""
    settings = JiraSettings(
        jira_url="https://test.atlassian.net",
        jira_email="user@example.com",
        jira_api_token="secret-token"
    )
    auth = settings.get_jira_auth()

    assert auth == ("user@example.com", "secret-token")
    assert isinstance(auth, tuple)
    assert len(auth) == 2


def test_jira_settings_immutable_after_creation():
    """Test that JiraSettings can be modified (Pydantic allows it by default)."""
    settings = JiraSettings(
        jira_url="https://test.atlassian.net",
        jira_email="test@example.com",
        jira_api_token="test-token"
    )

    # Pydantic models are mutable by default
    settings.jira_url = "https://new.atlassian.net"
    assert settings.jira_url == "https://new.atlassian.net"


def test_jira_settings_extra_fields_allowed():
    """Test that extra fields are allowed and ignored by Pydantic."""
    # Pydantic allows extra fields but ignores them
    settings = JiraSettings(
        jira_url="https://test.atlassian.net",
        jira_email="test@example.com",
        jira_api_token="test-token",
        extra_field="this_is_ignored"
    )

    # Extra field should not be present
    assert not hasattr(settings, 'extra_field')
    assert settings.jira_url == "https://test.atlassian.net"


def test_jira_settings_model_dump():
    """Test converting settings to dictionary."""
    settings = JiraSettings(
        jira_url="https://test.atlassian.net",
        jira_email="test@example.com",
        jira_api_token="test-token-123"
    )

    config_dict = settings.model_dump()
    assert config_dict["jira_url"] == "https://test.atlassian.net"
    assert config_dict["jira_email"] == "test@example.com"
    assert config_dict["jira_api_token"] == "test-token-123"


def test_jira_settings_model_dump_json():
    """Test converting settings to JSON."""
    settings = JiraSettings(
        jira_url="https://test.atlassian.net",
        jira_email="test@example.com",
        jira_api_token="test-token-123"
    )

    json_str = settings.model_dump_json()
    assert isinstance(json_str, str)
    assert "https://test.atlassian.net" in json_str
    assert "test@example.com" in json_str
