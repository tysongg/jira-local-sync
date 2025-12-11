from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JiraSettings(BaseSettings):
    """Jira connection settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

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
        """Return authentication tuple for Jira client."""
        return (self.jira_email, self.jira_api_token)
