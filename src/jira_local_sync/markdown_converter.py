"""Convert Jira issues to Markdown format."""

import logging
from datetime import datetime
from typing import Any

from jira2markdown import convert as jira_to_md

logger = logging.getLogger(__name__)


class MarkdownConverter:
    """Convert Jira issues to Markdown format."""

    def __init__(self):
        """Initialize the markdown converter."""
        pass

    def convert_jira_markup(self, text: str | None) -> str:
        """Convert Jira markup text to Markdown.

        Args:
            text: Jira markup text to convert

        Returns:
            Converted markdown text
        """
        if not text:
            return ""

        try:
            return jira_to_md(text)
        except Exception as e:
            logger.warning(f"Failed to convert Jira markup: {e}")
            # Fallback: return original text
            return text

    def format_issue_metadata(self, issue: Any) -> str:
        """Format issue metadata as Markdown frontmatter.

        Args:
            issue: Jira issue object

        Returns:
            Formatted metadata string
        """
        fields = issue.fields
        metadata_lines = []

        # Basic info
        metadata_lines.append(f"**Key:** {issue.key}")
        metadata_lines.append(f"**Type:** {fields.issuetype.name}")
        metadata_lines.append(f"**Status:** {fields.status.name}")

        # Priority
        if hasattr(fields, 'priority') and fields.priority:
            metadata_lines.append(f"**Priority:** {fields.priority.name}")

        # People
        if hasattr(fields, 'assignee') and fields.assignee:
            metadata_lines.append(f"**Assignee:** {fields.assignee.displayName}")
        else:
            metadata_lines.append("**Assignee:** Unassigned")

        if hasattr(fields, 'reporter') and fields.reporter:
            metadata_lines.append(f"**Reporter:** {fields.reporter.displayName}")

        # Dates
        if hasattr(fields, 'created'):
            created = self._format_date(fields.created)
            metadata_lines.append(f"**Created:** {created}")

        if hasattr(fields, 'updated'):
            updated = self._format_date(fields.updated)
            metadata_lines.append(f"**Updated:** {updated}")

        # Epic link
        if hasattr(fields, 'parent') and fields.parent:
            metadata_lines.append(f"**Parent:** [{fields.parent.key}] {fields.parent.fields.summary}")

        # Sprint
        if hasattr(fields, 'sprint') and fields.sprint:
            metadata_lines.append(f"**Sprint:** {fields.sprint.name}")

        # Labels
        if hasattr(fields, 'labels') and fields.labels:
            labels = " ".join([f"`{label}`" for label in fields.labels])
            metadata_lines.append(f"**Labels:** {labels}")

        return "\n".join(metadata_lines)

    def format_issue_description(self, issue: Any) -> str:
        """Format issue description section.

        Args:
            issue: Jira issue object

        Returns:
            Formatted description markdown
        """
        description = issue.fields.description

        if not description:
            return "_No description provided._"

        return self.convert_jira_markup(description)

    def format_comments(self, comments: list[Any]) -> str:
        """Format issue comments as Markdown.

        Args:
            comments: List of Jira comment objects

        Returns:
            Formatted comments markdown
        """
        if not comments:
            return "_No comments._"

        comment_lines = []

        for comment in comments:
            author = comment.author.displayName if hasattr(comment, 'author') else "Unknown"
            created = self._format_date(comment.created) if hasattr(comment, 'created') else "Unknown date"
            body = self.convert_jira_markup(comment.body)

            comment_lines.append(f"### {author} - {created}")
            comment_lines.append("")
            comment_lines.append(body)
            comment_lines.append("")

        return "\n".join(comment_lines)

    def format_attachments(self, issue: Any) -> str:
        """Format issue attachments as Markdown links.

        Args:
            issue: Jira issue object

        Returns:
            Formatted attachments markdown
        """
        if not hasattr(issue.fields, 'attachment') or not issue.fields.attachment:
            return "_No attachments._"

        attachment_lines = []

        for attachment in issue.fields.attachment:
            name = attachment.filename
            url = attachment.content if hasattr(attachment, 'content') else "#"
            size = self._format_file_size(attachment.size) if hasattr(attachment, 'size') else "Unknown size"

            attachment_lines.append(f"- [{name}]({url}) ({size})")

        return "\n".join(attachment_lines)

    def issue_to_markdown(
        self,
        issue: Any,
        comments: list[Any] | None = None,
        include_comments: bool = True,
        include_attachments: bool = True,
    ) -> str:
        """Convert a complete Jira issue to Markdown.

        Args:
            issue: Jira issue object
            comments: Optional list of comment objects
            include_comments: Whether to include comments section
            include_attachments: Whether to include attachments section

        Returns:
            Complete markdown document for the issue
        """
        sections = []

        # Title
        sections.append(f"# [{issue.key}] {issue.fields.summary}")
        sections.append("")

        # Metadata
        sections.append(self.format_issue_metadata(issue))
        sections.append("")

        # Description
        sections.append("## Description")
        sections.append("")
        sections.append(self.format_issue_description(issue))
        sections.append("")

        # Comments
        if include_comments and comments:
            sections.append("## Comments")
            sections.append("")
            sections.append(self.format_comments(comments))
            sections.append("")

        # Attachments
        if include_attachments:
            sections.append("## Attachments")
            sections.append("")
            sections.append(self.format_attachments(issue))
            sections.append("")

        # Footer
        now = datetime.now().strftime("%Y-%m-%d")
        sections.append("---")
        sections.append(f"*Exported from Jira: {now}*")

        return "\n".join(sections)

    def _format_date(self, date_str: str) -> str:
        """Format a Jira date string to a readable format.

        Args:
            date_str: ISO format date string from Jira

        Returns:
            Formatted date string
        """
        try:
            # Jira returns dates in ISO format with timezone
            # Example: "2025-12-11T10:30:45.123-0400"
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return date_str

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
