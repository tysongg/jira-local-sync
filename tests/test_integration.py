"""Integration tests for Jira client with real Jira instance.

These tests require a .env file with valid Jira credentials.
Run with: uv run pytest -m integration
"""

import pytest
from pydantic import ValidationError

from src.jira_local_sync.config import JiraSettings
from src.jira_local_sync.jira_client import JiraClient


@pytest.fixture(scope="module")
def jira_settings():
    """Load Jira settings from .env file.

    This fixture is module-scoped to avoid reloading settings for each test.
    """
    try:
        return JiraSettings()
    except ValidationError as e:
        pytest.skip(
            f"Jira credentials not configured. Create a .env file with JIRA_URL, "
            f"JIRA_EMAIL, and JIRA_API_TOKEN. Error: {e}"
        )


@pytest.fixture(scope="module")
def jira_client(jira_settings):
    """Create a Jira client instance.

    This fixture is module-scoped to reuse the connection across tests.
    """
    return JiraClient(jira_settings)


@pytest.mark.integration
def test_configuration_loads(jira_settings):
    """Test that configuration loads from .env file."""
    assert jira_settings.jira_url
    assert jira_settings.jira_email
    assert jira_settings.jira_api_token
    assert jira_settings.jira_url.startswith("https://")


@pytest.mark.integration
def test_connection_successful(jira_client):
    """Test that connection to Jira instance succeeds."""
    info = jira_client.test_connection()

    assert info["connected"] is True
    assert "version" in info
    assert "url" in info
    assert info["url"] == jira_client.settings.jira_url


@pytest.mark.integration
def test_fetch_projects(jira_client):
    """Test fetching available projects."""
    projects = jira_client.client.projects()

    assert isinstance(projects, list)
    assert len(projects) > 0

    # Verify project structure
    first_project = projects[0]
    assert hasattr(first_project, 'key')
    assert hasattr(first_project, 'name')


@pytest.mark.integration
def test_search_issues_with_project_filter(jira_client):
    """Test searching for issues with project filter."""
    # Get first available project
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"

    issues = jira_client.search_issues(jql, max_results=5)

    assert isinstance(issues, list)
    # May be empty if project has no issues
    if issues:
        assert all(issue.fields.project.key == project_key for issue in issues)


@pytest.mark.integration
def test_search_issues_pagination(jira_client):
    """Test that pagination works correctly."""
    # Get a project with issues
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY created DESC"

    # Try to get more than one batch (if available)
    issues = jira_client.search_issues(jql, max_results=150)

    assert isinstance(issues, list)
    # Just verify we can handle pagination without errors


@pytest.mark.integration
def test_get_single_issue(jira_client):
    """Test fetching a single issue by key."""
    # First, find an issue to fetch
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"
    issues = jira_client.search_issues(jql, max_results=1)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    issue_key = issues[0].key

    # Fetch the issue
    issue = jira_client.get_issue(issue_key)

    assert issue.key == issue_key
    assert hasattr(issue.fields, 'summary')
    assert hasattr(issue.fields, 'status')
    assert hasattr(issue.fields, 'issuetype')


@pytest.mark.integration
def test_get_issue_with_specific_fields(jira_client):
    """Test fetching an issue with specific fields only."""
    # Find an issue
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"
    issues = jira_client.search_issues(jql, max_results=1)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    issue_key = issues[0].key

    # Fetch with specific fields
    issue = jira_client.get_issue(issue_key, fields=["summary", "status"])

    assert issue.key == issue_key
    assert hasattr(issue.fields, 'summary')
    assert hasattr(issue.fields, 'status')


@pytest.mark.integration
def test_get_issue_comments(jira_client):
    """Test fetching comments for an issue."""
    # Find an issue
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"
    issues = jira_client.search_issues(jql, max_results=5)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    issue_key = issues[0].key

    # Fetch comments
    comments = jira_client.get_issue_comments(issue_key)

    assert isinstance(comments, list)
    # Comments may be empty, which is fine
    if comments:
        first_comment = comments[0]
        assert hasattr(first_comment, 'body')
        assert hasattr(first_comment, 'author')


@pytest.mark.integration
def test_search_with_max_results_limit(jira_client):
    """Test that max_results parameter limits returned issues."""
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY created DESC"

    max_results = 3
    issues = jira_client.search_issues(jql, max_results=max_results)

    assert isinstance(issues, list)
    assert len(issues) <= max_results


@pytest.mark.integration
def test_search_empty_results(jira_client):
    """Test searching with query that returns no results."""
    # Use a query that might return no results (valid project but specific filter)
    projects = jira_client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    # Use a filter that's unlikely to match any issues
    jql = f"project = {project_key} AND summary ~ 'THISSHOULDNOTEXIST12345UNLIKELY'"

    # This should return an empty list, not raise an error
    issues = jira_client.search_issues(jql)
    assert isinstance(issues, list)
    assert len(issues) == 0
