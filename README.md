# Jira Local Sync

A Python library for exporting Jira issues to Markdown format with support for comments and attachments.

## Features

- 🔍 **Flexible JQL queries** - Fetch any issues matching your JQL query
- 📝 **Rich Markdown output** - Convert issues to well-formatted Markdown
- 💬 **Comments support** - Optionally include issue comments
- 📎 **Attachments tracking** - List attachments with metadata
- 🔄 **Streaming processing** - Memory-efficient generator-based API
- ⚙️ **Type-safe configuration** - Pydantic-based settings validation
- 🧪 **Well-tested** - Comprehensive unit and integration tests

## Installation

Install using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv pip install jira-local-sync
```

Or using pip:

```bash
pip install jira-local-sync
```

## Prerequisites

Before using this library, you'll need:

1. A Jira Cloud account
2. A Jira API token
3. Your Jira instance URL
4. Your Jira account email

## Getting Your Jira API Token

To authenticate with Jira, you need to generate an API token:

### Step 1: Navigate to Atlassian Account Security

1. Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Log in with your Atlassian account

### Step 2: Create an API Token

1. Click **"Create API token"**
2. Enter a label for your token (e.g., "Jira Local Sync")
3. Click **"Create"**
4. Copy the token immediately (you won't be able to see it again!)

### Step 3: Store Your Token Securely

⚠️ **Important**: Treat your API token like a password. Never commit it to version control!

Create a `.env` file in your project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
JIRA_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_api_token_here
```

## Quick Start

### Basic Usage

```python
from jira_local_sync import JiraSettings, JiraProcessor

# Configure settings
settings = JiraSettings(
    jira_url="https://yourcompany.atlassian.net",
    jira_email="your.email@company.com",
    jira_api_token="your_api_token_here",
)

# Initialize processor
processor = JiraProcessor(
    settings=settings,
    include_comments=True,
    include_attachments=True,
)

# Fetch and process issues
jql = "project = MYPROJECT AND type = Story"
for issue_key, markdown in processor.process_issues(jql):
    # Save to file
    with open(f"{issue_key}.md", "w") as f:
        f.write(markdown)
    print(f"✓ Saved {issue_key}")
```

### Using Environment Variables

```python
import os
from jira_local_sync import JiraSettings, JiraProcessor

# Load from environment variables
settings = JiraSettings(
    jira_url=os.environ["JIRA_URL"],
    jira_email=os.environ["JIRA_EMAIL"],
    jira_api_token=os.environ["JIRA_API_TOKEN"],
)

processor = JiraProcessor(settings)

# Process a single issue
issue_key, markdown = processor.process_single_issue("PROJ-123")
print(markdown)
```

### Advanced Usage

```python
from jira_local_sync import JiraClient, MarkdownConverter

# Lower-level API for more control
client = JiraClient(settings)
converter = MarkdownConverter()

# Search with specific fields
issues = client.search_issues(
    jql="project = MYPROJ",
    fields=["summary", "description", "status", "assignee"],
    max_results=50
)

# Convert each issue
for issue in issues:
    comments = client.get_issue_comments(issue.key)
    markdown = converter.issue_to_markdown(
        issue,
        comments=comments,
        include_comments=True,
        include_attachments=True,
    )
    print(markdown)
```

## Configuration

### JiraSettings

The `JiraSettings` class accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `jira_url` | `str` | Yes | Your Jira instance URL (e.g., `https://yourcompany.atlassian.net`) |
| `jira_email` | `str` | Yes | Email address associated with your Jira account |
| `jira_api_token` | `str` | Yes | Your Jira API token |

### JiraProcessor Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `settings` | `JiraSettings` | Required | Jira connection settings |
| `include_comments` | `bool` | `True` | Include comments in markdown output |
| `include_attachments` | `bool` | `True` | Include attachments section in markdown output |

## Examples

See the [examples/](examples/) directory for complete working examples:

- **[calypso_stories.py](examples/calypso_stories.py)** - Export all stories from a project

Run the example:

```bash
# Set environment variables or use .env file
export JIRA_URL="https://yourcompany.atlassian.net"
export JIRA_EMAIL="your.email@company.com"
export JIRA_API_TOKEN="your_api_token_here"

# Run the example
python examples/calypso_stories.py
```

## API Reference

### JiraProcessor

#### `process_issues(jql, fields=None, max_results=None)`

Process multiple issues matching a JQL query.

**Parameters:**
- `jql` (str): JQL query string
- `fields` (str | list[str] | None): Optional list of fields to fetch
- `max_results` (int | None): Maximum number of issues to process

**Yields:**
- `tuple[str, str]`: (issue_key, markdown_content) for each issue

#### `process_single_issue(issue_key, fields=None)`

Process a single issue by key.

**Parameters:**
- `issue_key` (str): Jira issue key (e.g., "PROJ-123")
- `fields` (str | list[str] | None): Optional list of fields to fetch

**Returns:**
- `tuple[str, str]`: (issue_key, markdown_content)

#### `test_connection()`

Test the connection to Jira.

**Returns:**
- `bool`: True if connection successful, False otherwise

### JiraClient

Lower-level client for direct Jira API access.

#### `search_issues(jql, fields=None, max_results=None)`

Search for issues using JQL.

#### `get_issue(issue_key, fields=None)`

Fetch a single issue by key.

#### `get_issue_comments(issue_key)`

Fetch comments for an issue.

### MarkdownConverter

Convert Jira issues to Markdown format.

#### `issue_to_markdown(issue, comments=None, include_comments=True, include_attachments=True)`

Convert a Jira issue to Markdown.

## Development

### Setup

1. Clone the repository:
```bash
git clone git@github.com:tysongg/jira-markdown.git
cd jira-local-sync
```

2. Install dependencies using [uv](https://docs.astral.sh/uv/):
```bash
uv sync --dev
```

3. Copy the environment file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Testing

Run all tests:
```bash
uv run pytest
```

Run only unit tests (no Jira connection required):
```bash
uv run pytest -m unit
```

Run integration tests (requires Jira credentials):
```bash
uv run pytest -m integration
```

Run with coverage:
```bash
uv run pytest --cov=src/jira_local_sync --cov-report=html
```

### Project Structure

```
jira-local-sync/
├── src/jira_local_sync/
│   ├── __init__.py          # Public API
│   ├── config.py            # Configuration settings
│   ├── jira_client.py       # Jira API client
│   ├── markdown_converter.py  # Markdown conversion
│   └── processor.py         # High-level orchestration
├── tests/
│   ├── unit/               # Unit tests (mocked)
│   └── integration/        # Integration tests (real Jira)
├── examples/               # Usage examples
└── docs/                   # Additional documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Security

- Never commit your `.env` file or expose your API token
- Rotate your API token regularly
- Use environment variables or secure secret management in production

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Authentication Errors

If you get authentication errors:

1. Verify your API token is correct and hasn't expired
2. Ensure your email matches your Jira account
3. Check that your Jira URL is correct (include `https://`)
4. Verify you have access to the projects you're querying

### Connection Issues

If you can't connect to Jira:

```python
# Test your connection
processor = JiraProcessor(settings)
if processor.test_connection():
    print("✓ Connected to Jira!")
else:
    print("✗ Connection failed")
```

### JQL Query Issues

- Validate your JQL in Jira's web interface first
- Use proper JQL syntax: `project = MYPROJ AND type = Story`
- Check field names match your Jira instance

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/tysongg/jira-markdown/issues)
- Check existing issues for solutions

## Acknowledgments

Built with:
- [jira-python](https://github.com/pycontribs/jira) - Jira API client
- [jira2markdown](https://github.com/valiton/jira2markdown) - Jira markup to Markdown conversion
- [pydantic](https://docs.pydantic.dev/) - Data validation
