from typing import Any
import logging
from jira import JIRA
from jira.exceptions import JIRAError

from .config import JiraSettings

logger = logging.getLogger(__name__)


class JiraClient:
    """Client for interacting with Jira API."""

    def __init__(self, settings: JiraSettings):
        """Initialize Jira client with settings.

        Args:
            settings: JiraSettings instance with connection details
        """
        self.settings = settings
        self._client: JIRA | None = None

    def connect(self) -> None:
        """Establish connection to Jira instance."""
        try:
            logger.info(f"Connecting to Jira at {self.settings.jira_url}")
            auth = self.settings.get_jira_auth()
            self._client = JIRA(
                server=self.settings.jira_url,
                basic_auth=auth,
            )
            # Test connection by getting server info
            server_info = self._client.server_info()
            logger.info(f"Connected to Jira version {server_info.get('version')}")
        except JIRAError as e:
            logger.error(f"Failed to connect to Jira: {e.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Jira: {e}")
            raise

    @property
    def client(self) -> JIRA:
        """Get the underlying JIRA client, connecting if needed."""
        if self._client is None:
            self.connect()
        assert self._client is not None
        return self._client

    def search_issues(
        self,
        jql: str,
        fields: str | list[str] | None = None,
        max_results: int | None = None,
    ) -> list[Any]:
        """Search for issues using JQL with automatic pagination.

        Args:
            jql: JQL query string
            fields: Fields to retrieve (default: all fields)
            max_results: Maximum number of results to return (default: all)

        Returns:
            List of issue objects
        """
        issues = []
        start_at = 0
        batch_size = 100  # Jira typical max per request

        logger.info(f"Executing JQL query: {jql}")

        try:
            while True:
                # Fetch batch of issues
                batch = self.client.search_issues(
                    jql_str=jql,
                    startAt=start_at,
                    maxResults=batch_size,
                    fields=fields,
                )

                if not batch:
                    break

                issues.extend(batch)
                logger.debug(f"Fetched {len(batch)} issues (total: {len(issues)})")

                # Check if we've reached max_results or all issues
                if max_results and len(issues) >= max_results:
                    issues = issues[:max_results]
                    break

                if len(batch) < batch_size:
                    # No more issues to fetch
                    break

                start_at += batch_size

            logger.info(f"Retrieved {len(issues)} issues total")
            return issues

        except JIRAError as e:
            logger.error(f"JQL query failed: {e.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise

    def get_issue(self, issue_key: str, fields: str | list[str] | None = None) -> Any:
        """Fetch a single issue by key.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            fields: Fields to retrieve (default: all fields)

        Returns:
            Issue object
        """
        try:
            logger.debug(f"Fetching issue {issue_key}")
            return self.client.issue(issue_key, fields=fields)
        except JIRAError as e:
            logger.error(f"Failed to fetch issue {issue_key}: {e.text}")
            raise

    def get_issue_comments(self, issue_key: str) -> list[Any]:
        """Fetch all comments for an issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")

        Returns:
            List of comment objects
        """
        try:
            logger.debug(f"Fetching comments for issue {issue_key}")
            return self.client.comments(issue_key)
        except JIRAError as e:
            logger.error(f"Failed to fetch comments for {issue_key}: {e.text}")
            raise

    def test_connection(self) -> dict[str, Any]:
        """Test the connection and return server information.

        Returns:
            Dictionary with server information
        """
        try:
            server_info = self.client.server_info()
            return {
                "connected": True,
                "url": self.settings.jira_url,
                "version": server_info.get("version"),
                "build_number": server_info.get("buildNumber"),
                "server_title": server_info.get("serverTitle"),
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
            }
