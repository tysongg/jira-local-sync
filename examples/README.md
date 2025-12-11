# Examples

This directory contains example applications demonstrating how to use the `jira-local-sync` library.

## calypso_stories.py

This example demonstrates how to:
1. Create a settings object from environment variables
2. Fetch all stories from the Calypso (CAL) project
3. Save each issue to a markdown file in the `./output/` directory

### Prerequisites

Make sure you have the required environment variables set. You can either:

1. **Set them directly in your shell:**
   ```bash
   export JIRA_URL="https://yourcompany.atlassian.net"
   export JIRA_EMAIL="your.email@company.com"
   export JIRA_API_TOKEN="your_api_token_here"
   ```

2. **Or create a `.env` file** in the project root (see `.env.example` for reference)

### Running the Example

From the project root directory:

```bash
python examples/calypso_stories.py
```

### What It Does

The example will:
- Load Jira credentials from environment variables
- Connect to your Jira instance
- Fetch all stories from the CAL project using JQL: `project = CAL AND type = Story ORDER BY key ASC`
- Convert each issue to Markdown format (including comments and attachments)
- Save each issue as `{issue_key}.md` in the `./output/` directory
- Display progress and summary information

### Output

Markdown files will be created in the `./output/` directory with names like:
- `CAL-1.md`
- `CAL-2.md`
- `CAL-3.md`
- etc.

Each file contains:
- Issue metadata (key, type, status, priority, assignee, dates, etc.)
- Description
- Comments
- Attachments list
- Export timestamp
