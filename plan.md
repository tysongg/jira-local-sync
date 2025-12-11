# Jira to Markdown Export Script - Implementation Plan

## Overview
Build a Python script that pulls issues, epics, and sprint data from Jira using JQL queries, converts the content to markdown, and saves one file per issue organized in folders.

## Architecture

### Core Components
1. **Configuration Module** (`config.py`)
   - Load settings from YAML config file
   - Store Jira URL, email, API token, JQL queries
   - Define output directory structure

2. **Jira Client Module** (`jira_client.py`)
   - Handle authentication with Jira API
   - Execute JQL queries with pagination
   - Fetch issue details, epic relationships, sprint data
   - Handle rate limiting and errors

3. **Markdown Converter Module** (`markdown_converter.py`)
   - Convert Jira markup to markdown format
   - Handle special formatting (code blocks, links, mentions)
   - Format issue metadata (status, assignee, dates, etc.)
   - Create markdown templates for different issue types

4. **File Manager Module** (`file_manager.py`)
   - Create output directory structure
   - Generate filenames from issue keys
   - Write markdown files with proper encoding
   - Organize files by project/type/epic

5. **Main Script** (`jira_to_markdown.py`)
   - Orchestrate the entire workflow
   - Display progress indicators
   - Implement logging
   - Handle errors gracefully

## Technology Stack

### Python Libraries
- **jira** (3.10.6+) - Official Jira API client with API token auth support
- **jira2markdown** (0.3.7+) - Convert Jira markup to markdown using parsing grammars
- **PyYAML** - Configuration file parsing
- **python-dotenv** - Environment variable management for credentials
- **tqdm** - Progress bars for long operations

### Alternative: Simple requests-based approach
If preferring minimal dependencies, can use `requests` library directly with Jira REST API

## Configuration File Structure

**config.yaml**
```yaml
jira:
  url: "https://yourcompany.atlassian.net"
  email: "${JIRA_EMAIL}"  # Reference to env variable
  api_token: "${JIRA_API_TOKEN}"  # Reference to env variable

queries:
  - name: "active_issues"
    jql: "project = MYPROJ AND status != Done"
  - name: "sprint_issues"
    jql: "project = MYPROJ AND sprint in openSprints()"

output:
  base_dir: "./jira_export"
  structure: "project_type"  # Options: project_type, epic, sprint, flat

options:
  include_comments: true
  include_attachments_info: true
  include_sprint_info: true
  include_epic_hierarchy: true
```

**.env** (gitignored)
```
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_api_token_here
```

## Output Directory Structure

```
jira_export/
├── PROJECT-NAME/
│   ├── epics/
│   │   ├── PROJ-123_epic-name.md
│   │   └── PROJ-456_another-epic.md
│   ├── stories/
│   │   ├── PROJ-124_story-title.md
│   │   └── PROJ-125_story-title.md
│   ├── tasks/
│   │   └── PROJ-126_task-title.md
│   └── bugs/
│       └── PROJ-127_bug-description.md
└── metadata.json  # Export metadata (date, query used, count)
```

## Markdown File Template

Each issue markdown file will contain:
```markdown
# [PROJ-123] Issue Title

**Status:** In Progress
**Type:** Story
**Priority:** High
**Assignee:** John Doe
**Reporter:** Jane Smith
**Created:** 2025-01-15
**Updated:** 2025-01-20

**Epic:** [PROJ-100] Epic Title
**Sprint:** Sprint 25

## Description

[Converted markdown content from Jira]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Comments

### John Doe - 2025-01-16 10:30
Comment text here...

### Jane Smith - 2025-01-18 14:20
Response text here...

## Linked Issues

- Blocks: [PROJ-124] Related Issue
- Relates to: [PROJ-125] Another Issue

## Labels

`backend` `api` `urgent`

---
*Exported from Jira: 2025-12-11*
```

## Implementation Steps

### Step 1: Project Setup
- Create project directory structure
- Set up `requirements.txt` with dependencies
- Create `.env.example` template
- Initialize config.yaml template

### Step 2: Configuration Module
- Implement YAML config loading
- Add environment variable substitution
- Validate required settings
- Create default config generator

### Step 3: Jira Client Module
- Implement API token authentication
- Create JQL query executor with pagination (Jira returns max 50-100 results per page)
- Add methods to fetch:
  - Issue details with all fields
  - Epic-story relationships (via `parent` link or epic link field)
  - Sprint information (from Agile API)
  - Comments and attachments metadata
- Implement retry logic and rate limiting

### Step 4: Markdown Converter Module
- Integrate jira2markdown library for text conversion
- Create issue metadata formatter
- Build template rendering for different issue types
- Handle special cases:
  - User mentions (@user → @user)
  - Issue links (PROJ-123 → [PROJ-123])
  - Code blocks (preserve formatting)
  - Tables and lists
  - Attachments (include links/references)

### Step 5: File Manager Module
- Create directory structure based on config
- Generate safe filenames from issue keys and summaries
- Implement file writing with UTF-8 encoding
- Add metadata.json export for tracking

### Step 6: Main Script
- Wire all modules together
- Add argparse for CLI options (--config, --output-dir, --query)
- Implement progress tracking with tqdm
- Add comprehensive logging (INFO, DEBUG, ERROR levels)
- Create error handling for common failures

### Step 7: Testing & Documentation
- Create README with setup instructions
- Document configuration options
- Add usage examples
- Include troubleshooting guide

## Key Considerations

### Jira API Specifics
- **Pagination:** Jira REST API returns max 50-100 results per request, use `startAt` parameter
- **Rate Limiting:** Jira Cloud has rate limits (typically 10,000 requests/day), implement backoff
- **Epic Links:** Epic-story relationships use `parent` field (v3 API) or custom `epic link` field (v2)
- **Sprint Field:** Sprint data comes from Agile/Software API, not standard REST API
- **Field Mapping:** Jira fields vary by instance, need to handle custom fields dynamically

### Error Handling
- Invalid credentials → Clear error message with setup instructions
- Network failures → Retry with exponential backoff
- Invalid JQL → Show Jira error message and suggest fix
- Missing permissions → List required permissions
- Large exports → Stream to disk, show progress

### Performance
- Fetch issues in batches (50-100 at a time)
- Use concurrent requests for independent operations
- Cache epic/sprint lookups to avoid redundant API calls
- Provide progress indicators for long-running exports

## Critical Files to Create

1. `jira_to_markdown.py` - Main entry point
2. `jira_client.py` - Jira API wrapper
3. `markdown_converter.py` - Markup conversion
4. `file_manager.py` - File operations
5. `config.py` - Configuration handling
6. `requirements.txt` - Dependencies
7. `config.yaml` - Configuration template
8. `.env.example` - Credentials template
9. `README.md` - Documentation

## Estimated File Count
~9 Python/config files + documentation = Complete solution

## Next Steps After Approval
1. Create project structure and requirements.txt
2. Implement configuration loading
3. Build Jira client with authentication
4. Develop markdown converter
5. Create file management system
6. Wire everything together in main script
7. Add logging and error handling
8. Test with real Jira instance
9. Document usage and setup
