"""High-level orchestration for processing Jira issues to Markdown."""

import logging
from typing import Iterator

from .config import JiraSettings
from .jira_client import JiraClient
from .markdown_converter import MarkdownConverter

logger = logging.getLogger(__name__)


class JiraProcessor:
    """High-level processor that orchestrates fetching issues and converting to Markdown.

    This class provides a convenient interface for applications to process Jira issues
    without needing to directly manage the client and converter separately.
    """

    def __init__(
        self,
        settings: JiraSettings,
        include_comments: bool = True,
        include_attachments: bool = True,
    ):
        """Initialize the processor.

        Args:
            settings: Jira connection settings
            include_comments: Whether to include comments in markdown output
            include_attachments: Whether to include attachments section in markdown output
        """
        self.settings = settings
        self.include_comments = include_comments
        self.include_attachments = include_attachments

        self.client = JiraClient(settings)
        self.converter = MarkdownConverter()

    def process_issues(
        self,
        jql: str,
        fields: str | list[str] | None = None,
        max_results: int | None = None,
    ) -> Iterator[tuple[str, str]]:
        """Process issues matching a JQL query and yield markdown documents.

        This is a generator that yields (issue_key, markdown_content) tuples as issues
        are fetched and converted. This allows applications to process issues one at a time
        without loading everything into memory.

        Args:
            jql: JQL query string to filter issues
            fields: Optional list of fields to fetch (default: all fields)
            max_results: Optional maximum number of issues to process

        Yields:
            Tuples of (issue_key, markdown_content) for each processed issue

        Example:
            >>> processor = JiraProcessor(settings)
            >>> for issue_key, markdown in processor.process_issues("project = MYPROJ"):
            ...     save_to_file(issue_key, markdown)
        """
        logger.info(f"Processing issues with JQL: {jql}")

        # Fetch issues (this handles pagination internally)
        issues = self.client.search_issues(jql, fields=fields, max_results=max_results)

        logger.info(f"Found {len(issues)} issues to process")

        # Process each issue
        for issue in issues:
            issue_key = issue.key
            logger.debug(f"Processing issue {issue_key}")

            # Fetch comments if requested
            comments = None
            if self.include_comments:
                try:
                    comments = self.client.get_issue_comments(issue_key)
                except Exception as e:
                    logger.warning(f"Failed to fetch comments for {issue_key}: {e}")
                    comments = []

            # Convert to markdown
            try:
                markdown = self.converter.issue_to_markdown(
                    issue,
                    comments=comments,
                    include_comments=self.include_comments,
                    include_attachments=self.include_attachments,
                )
                yield (issue_key, markdown)
                logger.debug(f"Successfully processed {issue_key}")
            except Exception as e:
                logger.error(f"Failed to convert {issue_key} to markdown: {e}")
                # Continue processing other issues even if one fails
                continue

    def process_single_issue(
        self,
        issue_key: str,
        fields: str | list[str] | None = None,
    ) -> tuple[str, str]:
        """Process a single issue by key and return markdown.

        Args:
            issue_key: Jira issue key (e.g., "PROJ-123")
            fields: Optional list of fields to fetch (default: all fields)

        Returns:
            Tuple of (issue_key, markdown_content)

        Raises:
            Exception: If issue fetch or conversion fails
        """
        logger.info(f"Processing single issue: {issue_key}")

        # Fetch the issue
        issue = self.client.get_issue(issue_key, fields=fields)

        # Fetch comments if requested
        comments = None
        if self.include_comments:
            try:
                comments = self.client.get_issue_comments(issue_key)
            except Exception as e:
                logger.warning(f"Failed to fetch comments for {issue_key}: {e}")
                comments = []

        # Convert to markdown
        markdown = self.converter.issue_to_markdown(
            issue,
            comments=comments,
            include_comments=self.include_comments,
            include_attachments=self.include_attachments,
        )

        logger.info(f"Successfully processed {issue_key}")
        return (issue_key, markdown)

    def test_connection(self) -> bool:
        """Test the connection to Jira.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            info = self.client.test_connection()
            return info["connected"]
        except Exception:
            return False
