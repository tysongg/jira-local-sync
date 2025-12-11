"""Tests for processor module."""

import pytest
from unittest.mock import Mock, patch

from src.jira_local_sync.config import JiraSettings
from src.jira_local_sync.processor import JiraProcessor

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return JiraSettings(
        jira_url="https://test.atlassian.net",
        jira_email="test@example.com",
        jira_api_token="test-token"
    )


@pytest.fixture
def mock_issue():
    """Create a mock Jira issue."""
    issue = Mock()
    issue.key = "TEST-123"
    issue.fields = Mock()
    issue.fields.summary = "Test Issue"
    issue.fields.description = "Test description"
    issue.fields.issuetype = Mock(name="Story")
    issue.fields.status = Mock(name="In Progress")
    issue.fields.priority = Mock(name="High")
    issue.fields.assignee = Mock(displayName="John Doe")
    issue.fields.reporter = Mock(displayName="Jane Smith")
    issue.fields.created = "2025-01-15T10:30:00.000-0500"
    issue.fields.updated = "2025-01-20T14:45:00.000-0500"
    issue.fields.labels = ["test"]
    issue.fields.attachment = []
    return issue


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_processor_initialization(mock_converter_class, mock_client_class, mock_settings):
    """Test JiraProcessor initializes correctly."""
    processor = JiraProcessor(mock_settings)

    assert processor.settings == mock_settings
    assert processor.include_comments is True
    assert processor.include_attachments is True
    mock_client_class.assert_called_once_with(mock_settings)
    mock_converter_class.assert_called_once()


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_processor_initialization_custom_options(mock_converter_class, mock_client_class, mock_settings):
    """Test JiraProcessor with custom options."""
    processor = JiraProcessor(
        mock_settings,
        include_comments=False,
        include_attachments=False
    )

    assert processor.include_comments is False
    assert processor.include_attachments is False


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_process_issues_success(mock_converter_class, mock_client_class, mock_settings, mock_issue):
    """Test processing issues successfully."""
    # Setup mocks
    mock_client = Mock()
    mock_client.search_issues.return_value = [mock_issue]
    mock_client.get_issue_comments.return_value = []
    mock_client_class.return_value = mock_client

    mock_converter = Mock()
    mock_converter.issue_to_markdown.return_value = "# Test Markdown"
    mock_converter_class.return_value = mock_converter

    # Create processor
    processor = JiraProcessor(mock_settings)

    # Process issues
    results = list(processor.process_issues("project = TEST"))

    # Verify results
    assert len(results) == 1
    assert results[0][0] == "TEST-123"
    assert results[0][1] == "# Test Markdown"

    # Verify calls
    mock_client.search_issues.assert_called_once_with("project = TEST", fields=None, max_results=None)
    mock_client.get_issue_comments.assert_called_once_with("TEST-123")
    mock_converter.issue_to_markdown.assert_called_once()


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_process_issues_multiple(mock_converter_class, mock_client_class, mock_settings):
    """Test processing multiple issues."""
    # Setup mocks
    issue1 = Mock(key="TEST-1")
    issue2 = Mock(key="TEST-2")
    issue3 = Mock(key="TEST-3")

    mock_client = Mock()
    mock_client.search_issues.return_value = [issue1, issue2, issue3]
    mock_client.get_issue_comments.return_value = []
    mock_client_class.return_value = mock_client

    mock_converter = Mock()
    mock_converter.issue_to_markdown.return_value = "# Markdown"
    mock_converter_class.return_value = mock_converter

    # Process
    processor = JiraProcessor(mock_settings)
    results = list(processor.process_issues("project = TEST"))

    # Verify
    assert len(results) == 3
    assert results[0][0] == "TEST-1"
    assert results[1][0] == "TEST-2"
    assert results[2][0] == "TEST-3"


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_process_issues_without_comments(mock_converter_class, mock_client_class, mock_settings, mock_issue):
    """Test processing issues without fetching comments."""
    mock_client = Mock()
    mock_client.search_issues.return_value = [mock_issue]
    mock_client_class.return_value = mock_client

    mock_converter = Mock()
    mock_converter.issue_to_markdown.return_value = "# Markdown"
    mock_converter_class.return_value = mock_converter

    # Create processor without comments
    processor = JiraProcessor(mock_settings, include_comments=False)
    results = list(processor.process_issues("project = TEST"))

    # Should not fetch comments
    mock_client.get_issue_comments.assert_not_called()

    # Should still convert with comments=None
    assert len(results) == 1


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_process_issues_comment_fetch_failure(mock_converter_class, mock_client_class, mock_settings, mock_issue):
    """Test processing continues when comment fetch fails."""
    mock_client = Mock()
    mock_client.search_issues.return_value = [mock_issue]
    mock_client.get_issue_comments.side_effect = Exception("Comment fetch failed")
    mock_client_class.return_value = mock_client

    mock_converter = Mock()
    mock_converter.issue_to_markdown.return_value = "# Markdown"
    mock_converter_class.return_value = mock_converter

    processor = JiraProcessor(mock_settings)
    results = list(processor.process_issues("project = TEST"))

    # Should still process issue with empty comments
    assert len(results) == 1


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_process_issues_conversion_failure_continues(mock_converter_class, mock_client_class, mock_settings):
    """Test processing continues when one issue conversion fails."""
    issue1 = Mock(key="TEST-1")
    issue2 = Mock(key="TEST-2")

    mock_client = Mock()
    mock_client.search_issues.return_value = [issue1, issue2]
    mock_client.get_issue_comments.return_value = []
    mock_client_class.return_value = mock_client

    mock_converter = Mock()
    # First conversion fails, second succeeds
    mock_converter.issue_to_markdown.side_effect = [
        Exception("Conversion failed"),
        "# Markdown 2"
    ]
    mock_converter_class.return_value = mock_converter

    processor = JiraProcessor(mock_settings)
    results = list(processor.process_issues("project = TEST"))

    # Should only have second issue
    assert len(results) == 1
    assert results[0][0] == "TEST-2"


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_process_single_issue_success(mock_converter_class, mock_client_class, mock_settings, mock_issue):
    """Test processing a single issue by key."""
    mock_client = Mock()
    mock_client.get_issue.return_value = mock_issue
    mock_client.get_issue_comments.return_value = []
    mock_client_class.return_value = mock_client

    mock_converter = Mock()
    mock_converter.issue_to_markdown.return_value = "# Test Markdown"
    mock_converter_class.return_value = mock_converter

    processor = JiraProcessor(mock_settings)
    issue_key, markdown = processor.process_single_issue("TEST-123")

    assert issue_key == "TEST-123"
    assert markdown == "# Test Markdown"
    mock_client.get_issue.assert_called_once_with("TEST-123", fields=None)


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_process_single_issue_with_fields(mock_converter_class, mock_client_class, mock_settings, mock_issue):
    """Test processing single issue with specific fields."""
    mock_client = Mock()
    mock_client.get_issue.return_value = mock_issue
    mock_client.get_issue_comments.return_value = []
    mock_client_class.return_value = mock_client

    mock_converter = Mock()
    mock_converter.issue_to_markdown.return_value = "# Markdown"
    mock_converter_class.return_value = mock_converter

    processor = JiraProcessor(mock_settings)
    processor.process_single_issue("TEST-123", fields=["summary", "status"])

    mock_client.get_issue.assert_called_once_with("TEST-123", fields=["summary", "status"])


@patch('src.jira_local_sync.processor.JiraClient')
def test_test_connection_success(mock_client_class, mock_settings):
    """Test connection test returns True on success."""
    mock_client = Mock()
    mock_client.test_connection.return_value = {"connected": True}
    mock_client_class.return_value = mock_client

    processor = JiraProcessor(mock_settings)
    result = processor.test_connection()

    assert result is True


@patch('src.jira_local_sync.processor.JiraClient')
def test_test_connection_failure(mock_client_class, mock_settings):
    """Test connection test returns False on failure."""
    mock_client = Mock()
    mock_client.test_connection.side_effect = Exception("Connection failed")
    mock_client_class.return_value = mock_client

    processor = JiraProcessor(mock_settings)
    result = processor.test_connection()

    assert result is False


@patch('src.jira_local_sync.processor.JiraClient')
@patch('src.jira_local_sync.processor.MarkdownConverter')
def test_process_issues_is_generator(mock_converter_class, mock_client_class, mock_settings):
    """Test that process_issues returns a generator."""
    mock_client = Mock()
    mock_client.search_issues.return_value = []
    mock_client_class.return_value = mock_client

    processor = JiraProcessor(mock_settings)
    result = processor.process_issues("project = TEST")

    # Should be a generator
    import types
    assert isinstance(result, types.GeneratorType)
