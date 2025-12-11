"""Integration tests for processor with real Jira instance."""

import os
import pytest
from pydantic import ValidationError

from src.jira_local_sync.config import JiraSettings
from src.jira_local_sync.processor import JiraProcessor

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def jira_settings():
    """Load Jira settings from environment variables."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")

    if not all([jira_url, jira_email, jira_api_token]):
        pytest.skip(
            "Jira credentials not configured. Set JIRA_URL, JIRA_EMAIL, "
            "and JIRA_API_TOKEN environment variables or create a .env file."
        )

    try:
        return JiraSettings(
            jira_url=jira_url,
            jira_email=jira_email,
            jira_api_token=jira_api_token
        )
    except ValidationError as e:
        pytest.skip(f"Invalid Jira credentials: {e}")


def test_processor_initialization(jira_settings):
    """Test that processor initializes correctly."""
    processor = JiraProcessor(jira_settings)

    assert processor.settings == jira_settings
    assert processor.client is not None
    assert processor.converter is not None


def test_processor_test_connection(jira_settings):
    """Test connection test method."""
    processor = JiraProcessor(jira_settings)

    result = processor.test_connection()
    assert result is True


def test_process_issues_with_real_jira(jira_settings):
    """Test processing real issues from Jira."""
    processor = JiraProcessor(jira_settings)

    # Get projects to build a valid query
    projects = processor.client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"

    # Process up to 3 issues
    results = []
    for issue_key, markdown in processor.process_issues(jql, max_results=3):
        results.append((issue_key, markdown))

    # Verify we got results
    assert len(results) > 0
    assert len(results) <= 3

    # Verify structure of results
    for issue_key, markdown in results:
        assert isinstance(issue_key, str)
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert issue_key in markdown
        assert "# [" in markdown
        assert "## Description" in markdown


def test_process_issues_generator_behavior(jira_settings):
    """Test that process_issues yields results one at a time."""
    processor = JiraProcessor(jira_settings)

    projects = processor.client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"

    # Get generator
    gen = processor.process_issues(jql, max_results=2)

    # Should be able to get first item
    first = next(gen, None)
    assert first is not None
    assert len(first) == 2

    # Should be able to get second item (if available)
    second = next(gen, None)
    # May or may not exist depending on project


def test_process_single_issue(jira_settings):
    """Test processing a single issue by key."""
    processor = JiraProcessor(jira_settings)

    # Find an issue to process
    projects = processor.client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"
    issues = processor.client.search_issues(jql, max_results=1)

    if not issues:
        pytest.skip(f"No issues found in project {project_key}")

    test_issue_key = issues[0].key

    # Process single issue
    issue_key, markdown = processor.process_single_issue(test_issue_key)

    # Verify results
    assert issue_key == test_issue_key
    assert isinstance(markdown, str)
    assert len(markdown) > 0
    assert test_issue_key in markdown
    assert "# [" in markdown


def test_process_issues_without_comments(jira_settings):
    """Test processing issues without fetching comments."""
    processor = JiraProcessor(jira_settings, include_comments=False)

    projects = processor.client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"

    results = list(processor.process_issues(jql, max_results=1))

    assert len(results) > 0
    # Markdown should still be generated
    assert isinstance(results[0][1], str)


def test_process_issues_without_attachments(jira_settings):
    """Test processing issues without attachments section."""
    processor = JiraProcessor(jira_settings, include_attachments=False)

    projects = processor.client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"

    results = list(processor.process_issues(jql, max_results=1))

    assert len(results) > 0
    # Markdown should still be generated
    assert isinstance(results[0][1], str)


def test_process_issues_with_specific_fields(jira_settings):
    """Test processing issues with specific fields.

    Note: When requesting specific fields, users must include all fields needed
    for markdown conversion (issuetype, status, summary, etc.). Otherwise
    conversion will fail and issues will be skipped.
    """
    processor = JiraProcessor(jira_settings)

    projects = processor.client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    jql = f"project = {project_key} ORDER BY updated DESC"

    # Request fields including required ones for conversion
    results = list(processor.process_issues(
        jql,
        fields=["summary", "status", "issuetype", "description", "created", "updated"],
        max_results=1
    ))

    # Should work when required fields are included
    assert len(results) > 0
    assert isinstance(results[0][1], str)


def test_process_empty_query_results(jira_settings):
    """Test processing when query returns no results."""
    processor = JiraProcessor(jira_settings)

    projects = processor.client.client.projects()
    if not projects:
        pytest.skip("No projects available")

    project_key = projects[0].key
    # Query that should return no results
    jql = f"project = {project_key} AND summary ~ 'THISSHOULDDEFINITELYNOTEXIST12345'"

    results = list(processor.process_issues(jql))

    # Should return empty list, not error
    assert results == []
