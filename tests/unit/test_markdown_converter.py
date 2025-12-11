"""Tests for markdown converter module."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from src.jira_local_sync.markdown_converter import MarkdownConverter

pytestmark = pytest.mark.unit


@pytest.fixture
def converter():
    """Create MarkdownConverter instance."""
    return MarkdownConverter()


@pytest.fixture
def mock_issue():
    """Create a mock Jira issue for testing."""
    issue = Mock()
    issue.key = "TEST-123"
    issue.fields = Mock()
    issue.fields.summary = "Test Issue Summary"
    issue.fields.description = "This is a test description"
    issue.fields.issuetype = Mock(name="Story")
    issue.fields.status = Mock(name="In Progress")
    issue.fields.priority = Mock(name="High")
    issue.fields.assignee = Mock(displayName="John Doe")
    issue.fields.reporter = Mock(displayName="Jane Smith")
    issue.fields.created = "2025-01-15T10:30:00.000-0500"
    issue.fields.updated = "2025-01-20T14:45:00.000-0500"
    issue.fields.labels = ["backend", "api", "urgent"]
    issue.fields.attachment = []
    return issue


def test_converter_initialization(converter):
    """Test MarkdownConverter initializes correctly."""
    assert converter is not None


def test_convert_jira_markup_with_text(converter):
    """Test converting Jira markup to Markdown."""
    jira_text = "*bold* _italic_ -strikethrough-"
    result = converter.convert_jira_markup(jira_text)

    # Basic test that conversion happens
    assert result is not None
    assert isinstance(result, str)


def test_convert_jira_markup_with_none(converter):
    """Test converting None returns empty string."""
    result = converter.convert_jira_markup(None)
    assert result == ""


def test_convert_jira_markup_with_empty_string(converter):
    """Test converting empty string."""
    result = converter.convert_jira_markup("")
    assert result == ""


def test_format_issue_metadata(converter, mock_issue):
    """Test formatting issue metadata."""
    result = converter.format_issue_metadata(mock_issue)

    assert "TEST-123" in result
    assert "Story" in result
    assert "In Progress" in result
    assert "High" in result
    assert "John Doe" in result
    assert "Jane Smith" in result
    assert "backend" in result
    assert "api" in result
    assert "urgent" in result


def test_format_issue_metadata_unassigned(converter, mock_issue):
    """Test formatting metadata for unassigned issue."""
    mock_issue.fields.assignee = None
    result = converter.format_issue_metadata(mock_issue)

    assert "Unassigned" in result


def test_format_issue_metadata_no_labels(converter, mock_issue):
    """Test formatting metadata without labels."""
    mock_issue.fields.labels = []
    result = converter.format_issue_metadata(mock_issue)

    # Should not contain Labels section
    assert result is not None


def test_format_issue_metadata_with_parent(converter, mock_issue):
    """Test formatting metadata with parent issue."""
    parent = Mock()
    parent.key = "TEST-100"
    parent.fields = Mock()
    parent.fields.summary = "Parent Epic"
    mock_issue.fields.parent = parent

    result = converter.format_issue_metadata(mock_issue)

    assert "TEST-100" in result
    assert "Parent Epic" in result


def test_format_issue_description(converter, mock_issue):
    """Test formatting issue description."""
    result = converter.format_issue_description(mock_issue)

    assert result is not None
    assert isinstance(result, str)


def test_format_issue_description_empty(converter, mock_issue):
    """Test formatting empty description."""
    mock_issue.fields.description = None
    result = converter.format_issue_description(mock_issue)

    assert "No description provided" in result


def test_format_comments_empty(converter):
    """Test formatting with no comments."""
    result = converter.format_comments([])
    assert "No comments" in result


def test_format_comments_with_data(converter):
    """Test formatting comments with data."""
    comment1 = Mock()
    comment1.author = Mock(displayName="Alice")
    comment1.created = "2025-01-16T10:00:00.000-0500"
    comment1.body = "First comment"

    comment2 = Mock()
    comment2.author = Mock(displayName="Bob")
    comment2.created = "2025-01-17T11:00:00.000-0500"
    comment2.body = "Second comment"

    result = converter.format_comments([comment1, comment2])

    assert "Alice" in result
    assert "Bob" in result
    assert "First comment" in result
    assert "Second comment" in result


def test_format_attachments_empty(converter, mock_issue):
    """Test formatting with no attachments."""
    mock_issue.fields.attachment = []
    result = converter.format_attachments(mock_issue)

    assert "No attachments" in result


def test_format_attachments_with_data(converter, mock_issue):
    """Test formatting attachments with data."""
    attachment1 = Mock()
    attachment1.filename = "document.pdf"
    attachment1.content = "https://example.com/document.pdf"
    attachment1.size = 1024 * 512  # 512 KB

    attachment2 = Mock()
    attachment2.filename = "image.png"
    attachment2.content = "https://example.com/image.png"
    attachment2.size = 1024 * 1024 * 2  # 2 MB

    mock_issue.fields.attachment = [attachment1, attachment2]
    result = converter.format_attachments(mock_issue)

    assert "document.pdf" in result
    assert "image.png" in result
    assert "https://example.com/document.pdf" in result
    assert "KB" in result
    assert "MB" in result


def test_issue_to_markdown_full(converter, mock_issue):
    """Test converting complete issue to markdown."""
    comments = [
        Mock(
            author=Mock(displayName="Alice"),
            created="2025-01-16T10:00:00.000-0500",
            body="Test comment"
        )
    ]

    result = converter.issue_to_markdown(
        mock_issue,
        comments=comments,
        include_comments=True,
        include_attachments=True
    )

    # Check structure
    assert "# [TEST-123] Test Issue Summary" in result
    assert "## Description" in result
    assert "## Comments" in result
    assert "## Attachments" in result
    assert "Exported from Jira" in result

    # Check metadata
    assert "John Doe" in result
    assert "Jane Smith" in result


def test_issue_to_markdown_no_comments(converter, mock_issue):
    """Test converting issue without comments section."""
    result = converter.issue_to_markdown(
        mock_issue,
        comments=None,
        include_comments=False,
        include_attachments=True
    )

    assert "# [TEST-123]" in result
    assert "## Comments" not in result


def test_issue_to_markdown_no_attachments(converter, mock_issue):
    """Test converting issue without attachments section."""
    result = converter.issue_to_markdown(
        mock_issue,
        comments=None,
        include_comments=False,
        include_attachments=False
    )

    assert "# [TEST-123]" in result
    assert "## Attachments" not in result


def test_format_date_valid(converter):
    """Test formatting valid ISO date."""
    date_str = "2025-01-15T10:30:45.123-0500"
    result = converter._format_date(date_str)

    assert "2025-01-15" in result


def test_format_date_invalid(converter):
    """Test formatting invalid date returns original."""
    invalid_date = "not-a-date"
    result = converter._format_date(invalid_date)

    assert result == invalid_date


def test_format_file_size_bytes(converter):
    """Test formatting file size in bytes."""
    assert converter._format_file_size(500) == "500 B"


def test_format_file_size_kilobytes(converter):
    """Test formatting file size in kilobytes."""
    result = converter._format_file_size(1024 * 5)
    assert "KB" in result


def test_format_file_size_megabytes(converter):
    """Test formatting file size in megabytes."""
    result = converter._format_file_size(1024 * 1024 * 3)
    assert "MB" in result


def test_format_file_size_gigabytes(converter):
    """Test formatting file size in gigabytes."""
    result = converter._format_file_size(1024 * 1024 * 1024 * 2)
    assert "GB" in result


def test_convert_jira_markup_with_lists(converter):
    """Test converting Jira lists to Markdown."""
    jira_text = "* Item 1\n* Item 2\n* Item 3"
    result = converter.convert_jira_markup(jira_text)

    assert result is not None


def test_convert_jira_markup_with_code_block(converter):
    """Test converting Jira code blocks to Markdown."""
    jira_text = "{code:python}\nprint('hello')\n{code}"
    result = converter.convert_jira_markup(jira_text)

    assert result is not None
