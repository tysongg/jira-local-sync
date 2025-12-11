"""Tests for Jira client module."""

import pytest
from unittest.mock import Mock, MagicMock
from jira.exceptions import JIRAError

from src.jira_local_sync.config import JiraSettings
from src.jira_local_sync.jira_client import JiraClient

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_settings():
    """Create mock JiraSettings for testing."""
    settings = Mock(spec=JiraSettings)
    settings.jira_url = "https://test.atlassian.net"
    settings.jira_email = "test@example.com"
    settings.jira_api_token = "test-token"
    settings.get_jira_auth.return_value = ("test@example.com", "test-token")
    return settings


@pytest.fixture
def jira_client(mock_settings):
    """Create JiraClient instance with mock settings."""
    return JiraClient(mock_settings)


@pytest.fixture
def mock_jira_api(mocker):
    """Mock the JIRA API class."""
    return mocker.patch("src.jira_local_sync.jira_client.JIRA")


def test_jira_client_initialization(mock_settings):
    """Test JiraClient initializes correctly."""
    client = JiraClient(mock_settings)
    assert client.settings == mock_settings
    assert client._client is None


def test_connect_success(jira_client, mock_jira_api):
    """Test successful connection to Jira."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}
    mock_jira_api.return_value = mock_instance

    jira_client.connect()

    assert jira_client._client is not None
    mock_jira_api.assert_called_once_with(
        server="https://test.atlassian.net",
        basic_auth=("test@example.com", "test-token"),
    )
    mock_instance.server_info.assert_called_once()


def test_connect_jira_error(jira_client, mock_jira_api):
    """Test connection failure with JIRAError."""
    error = JIRAError(status_code=401, text="Unauthorized")
    mock_jira_api.side_effect = error

    with pytest.raises(JIRAError):
        jira_client.connect()


def test_client_property_lazy_connect(jira_client, mock_jira_api):
    """Test that client property connects if not already connected."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}
    mock_jira_api.return_value = mock_instance

    # First access should trigger connection
    client = jira_client.client
    assert client is not None
    mock_jira_api.assert_called_once()

    # Second access should not trigger another connection
    client2 = jira_client.client
    assert client2 is client
    assert mock_jira_api.call_count == 1


def test_search_issues_single_batch(jira_client, mock_jira_api):
    """Test searching issues with results fitting in single batch."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}

    # Create mock issues
    mock_issue1 = Mock()
    mock_issue1.key = "TEST-1"
    mock_issue2 = Mock()
    mock_issue2.key = "TEST-2"

    mock_instance.search_issues.return_value = [mock_issue1, mock_issue2]
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    results = jira_client.search_issues("project = TEST")

    assert len(results) == 2
    assert results[0].key == "TEST-1"
    assert results[1].key == "TEST-2"
    mock_instance.search_issues.assert_called_once()


def test_search_issues_pagination(jira_client, mock_jira_api):
    """Test searching issues with pagination."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}

    # Create 150 mock issues to trigger pagination
    batch1 = [Mock(key=f"TEST-{i}") for i in range(1, 101)]
    batch2 = [Mock(key=f"TEST-{i}") for i in range(101, 151)]

    mock_instance.search_issues.side_effect = [batch1, batch2]
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    results = jira_client.search_issues("project = TEST")

    assert len(results) == 150
    assert results[0].key == "TEST-1"
    assert results[149].key == "TEST-150"
    assert mock_instance.search_issues.call_count == 2


def test_search_issues_max_results(jira_client, mock_jira_api):
    """Test searching issues with max_results limit."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}

    # Return 100 issues but limit to 50
    batch = [Mock(key=f"TEST-{i}") for i in range(1, 101)]
    mock_instance.search_issues.return_value = batch
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    results = jira_client.search_issues("project = TEST", max_results=50)

    assert len(results) == 50
    assert results[0].key == "TEST-1"
    assert results[49].key == "TEST-50"


def test_search_issues_empty_results(jira_client, mock_jira_api):
    """Test searching issues with no results."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}
    mock_instance.search_issues.return_value = []
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    results = jira_client.search_issues("project = NONEXISTENT")

    assert len(results) == 0


def test_search_issues_jira_error(jira_client, mock_jira_api):
    """Test searching issues with JQL error."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}
    error = JIRAError(status_code=400, text="Invalid JQL")
    mock_instance.search_issues.side_effect = error
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    with pytest.raises(JIRAError):
        jira_client.search_issues("invalid JQL syntax")


def test_get_issue_success(jira_client, mock_jira_api):
    """Test getting a single issue successfully."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}

    mock_issue = Mock()
    mock_issue.key = "TEST-123"
    mock_issue.fields.summary = "Test issue"
    mock_instance.issue.return_value = mock_issue

    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    issue = jira_client.get_issue("TEST-123")

    assert issue.key == "TEST-123"
    assert issue.fields.summary == "Test issue"
    mock_instance.issue.assert_called_once_with("TEST-123", fields=None)


def test_get_issue_with_fields(jira_client, mock_jira_api):
    """Test getting an issue with specific fields."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}
    mock_instance.issue.return_value = Mock()
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    jira_client.get_issue("TEST-123", fields=["summary", "status"])

    mock_instance.issue.assert_called_once_with(
        "TEST-123", fields=["summary", "status"]
    )


def test_get_issue_not_found(jira_client, mock_jira_api):
    """Test getting a non-existent issue."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}
    error = JIRAError(status_code=404, text="Issue not found")
    mock_instance.issue.side_effect = error
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    with pytest.raises(JIRAError):
        jira_client.get_issue("TEST-999")


def test_get_issue_comments(jira_client, mock_jira_api):
    """Test getting comments for an issue."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {"version": "9.0.0"}

    mock_comment1 = Mock()
    mock_comment1.body = "First comment"
    mock_comment2 = Mock()
    mock_comment2.body = "Second comment"

    mock_instance.comments.return_value = [mock_comment1, mock_comment2]
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    comments = jira_client.get_issue_comments("TEST-123")

    assert len(comments) == 2
    assert comments[0].body == "First comment"
    assert comments[1].body == "Second comment"
    mock_instance.comments.assert_called_once_with("TEST-123")


def test_test_connection_success(jira_client, mock_jira_api):
    """Test connection test returns success info."""
    mock_instance = Mock()
    mock_instance.server_info.return_value = {
        "version": "9.0.0",
        "buildNumber": "12345",
        "serverTitle": "Test Jira",
    }
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    info = jira_client.test_connection()

    assert info["connected"] is True
    assert info["url"] == "https://test.atlassian.net"
    assert info["version"] == "9.0.0"
    assert info["build_number"] == "12345"
    assert info["server_title"] == "Test Jira"


def test_test_connection_failure(jira_client, mock_jira_api):
    """Test connection test returns failure info."""
    mock_instance = Mock()
    mock_instance.server_info.side_effect = Exception("Connection failed")
    mock_jira_api.return_value = mock_instance
    jira_client._client = mock_instance

    info = jira_client.test_connection()

    assert info["connected"] is False
    assert "error" in info
    assert "Connection failed" in info["error"]
