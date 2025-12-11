from pydantic import BaseModel, Field


class JiraSettings(BaseModel):
    """Jira connection settings.

    This is a plain data model. Applications using this library are responsible
    for loading configuration from environment variables, files, or other sources.
    """

    jira_url: str = Field(
        description="Jira instance URL (e.g., https://yourcompany.atlassian.net)"
    )
    jira_email: str = Field(
        description="Email address for Jira authentication"
    )
    jira_api_token: str = Field(
        description="API token for Jira authentication"
    )

    def get_jira_auth(self) -> tuple[str, str]:
        """Return authentication tuple for Jira client.

        Returns:
            Tuple of (email, api_token) for basic auth
        """
        return (self.jira_email, self.jira_api_token)
