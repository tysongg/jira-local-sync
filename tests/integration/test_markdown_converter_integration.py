"""Integration tests for markdown converter with real Jira issues."""

import os
import pytest
from pydantic import ValidationError

from src.jira_local_sync.config import JiraSettings
from src.jira_local_sync.jira_client import JiraClient
from src.jira_local_sync.markdown_converter import MarkdownConverter

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def jira_settings():
    """Load Jira settings from environment variables."""
    # Load .env file if it exists (simulating what an application would do)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not available, use environment as-is

    # Get credentials from environment
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")

    # Skip if not configured
    if not all([jira_url, jira_email, jira_api_token]):
        pytest.skip(
            "Jira credentials not configured. Set JIRA_URL, JIRA_EMAIL, "
            "and JIRA_API_TOKEN environment variables or create a .env file."
        )

    # Create settings using the library's data model
    try:
        return JiraSettings(
            jira_url=jira_url,
            jira_email=jira_email,
            jira_api_token=jira_api_token
        )
    except ValidationError as e:
        pytest.skip(f"Invalid Jira credentials: {e}")


@pytest.fixture(scope="module")
def jira_client(jira_settings):
    """Create a Jira client instance."""
    return JiraClient(jira_settings)


@pytest.fixture(scope="module")
def converter():
    """Create a MarkdownConverter instance."""
    return MarkdownConverter()


def test_convert_real_issue_to_markdown(jira_client, converter):
    """Test converting a real Jira issue to markdown."""
    # Get a real issue
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"
    issues = jira_client.search_issues(jql, max_results=1)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    issue = issues[0]

    # Get comments
    comments = jira_client.get_issue_comments(issue.key)

    # Convert to markdown
    markdown = converter.issue_to_markdown(
        issue,
        comments=comments,
        include_comments=True,
        include_attachments=True
    )

    # Verify markdown structure
    assert markdown is not None
    assert isinstance(markdown, str)
    assert len(markdown) > 0

    # Check for key elements
    assert f"[{issue.key}]" in markdown
    assert issue.fields.summary in markdown
    assert "## Description" in markdown
    assert "Exported from Jira" in markdown

    # Verify metadata is present
    assert issue.fields.issuetype.name in markdown
    assert issue.fields.status.name in markdown


def test_convert_issue_with_jira_markup(jira_client, converter):
    """Test converting an issue that contains Jira markup."""
    # Get an issue
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY created DESC"
    issues = jira_client.search_issues(jql, max_results=5)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    # Find an issue with a description (most likely to have markup)
    issue_with_description = None
    for issue in issues:
        if issue.fields.description:
            issue_with_description = issue
            break

    if not issue_with_description:
        pytest.skip("No issues with descriptions found")

    # Convert description
    markdown_desc = converter.format_issue_description(issue_with_description)

    # Should return some content
    assert markdown_desc is not None
    assert isinstance(markdown_desc, str)
    assert len(markdown_desc) > 0
    assert "No description provided" not in markdown_desc


def test_convert_issue_metadata(jira_client, converter):
    """Test converting real issue metadata."""
    # Get a real issue
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"
    issues = jira_client.search_issues(jql, max_results=1)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    issue = issues[0]

    # Format metadata
    metadata = converter.format_issue_metadata(issue)

    # Verify key metadata fields
    assert issue.key in metadata
    assert issue.fields.issuetype.name in metadata
    assert issue.fields.status.name in metadata

    # Check for dates
    assert "Created:" in metadata or "Updated:" in metadata


def test_convert_real_comments(jira_client, converter):
    """Test converting real Jira comments."""
    # Get an issue
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"
    issues = jira_client.search_issues(jql, max_results=10)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    # Find an issue with comments
    issue_with_comments = None
    for issue in issues:
        comments = jira_client.get_issue_comments(issue.key)
        if comments:
            issue_with_comments = issue
            break

    if not issue_with_comments:
        pytest.skip("No issues with comments found")

    # Get and format comments
    comments = jira_client.get_issue_comments(issue_with_comments.key)
    formatted_comments = converter.format_comments(comments)

    # Verify comments were formatted
    assert formatted_comments is not None
    assert "No comments" not in formatted_comments
    assert len(formatted_comments) > 0


def test_full_markdown_output_structure(jira_client, converter):
    """Test that full markdown output has proper structure."""
    # Get a real issue
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"
    issues = jira_client.search_issues(jql, max_results=1)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    issue = issues[0]
    comments = jira_client.get_issue_comments(issue.key)

    # Convert to full markdown
    markdown = converter.issue_to_markdown(issue, comments=comments)

    # Check markdown structure
    lines = markdown.split('\n')

    # First line should be title with issue key
    assert lines[0].startswith('#')
    assert issue.key in lines[0]

    # Should have section headers
    assert '## Description' in markdown
    assert '## Comments' in markdown
    assert '## Attachments' in markdown

    # Should have footer
    assert '---' in markdown
    assert 'Exported from Jira' in markdown
