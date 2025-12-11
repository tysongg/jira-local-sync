# Jira to Markdown Export Library - Implementation Plan

## Overview
Build a Python library that pulls issues, epics, and sprint data from Jira using JQL queries, converts the content to markdown, and saves one file per issue organized in folders.

**Note:** This is a library, not a standalone script. Applications using this library are responsible for loading configuration and orchestrating the workflow.

## Architecture

### Core Components

1. **✅ Configuration Module** (`config.py`) - **COMPLETED**
   - Plain Pydantic BaseModel for Jira connection settings
   - Store Jira URL, email, API token
   - Applications are responsible for loading configuration from environment, files, etc.
   - **Implementation:** Plain `JiraSettings(BaseModel)` with validation

2. **✅ Jira Client Module** (`jira_client.py`) - **COMPLETED**
   - Handle authentication with Jira API
   - Execute JQL queries with pagination
   - Fetch issue details, epic relationships, sprint data
   - Handle rate limiting and errors
   - **Implementation:**
     - `JiraClient` class with lazy connection
     - Automatic pagination for search results
     - Methods: `search_issues()`, `get_issue()`, `get_issue_comments()`, `test_connection()`

3. **✅ Markdown Converter Module** (`markdown_converter.py`) - **COMPLETED**
   - Convert Jira markup to markdown format using jira2markdown library
   - Handle special formatting (code blocks, links, mentions)
   - Format issue metadata (status, assignee, dates, etc.)
   - Create markdown templates for different issue types
   - **Implementation:**
     - `MarkdownConverter` class
     - Methods: `issue_to_markdown()`, `format_issue_metadata()`, `format_comments()`, etc.
     - Date and file size formatting utilities

4. **File Manager Module** (`file_manager.py`) - **TODO**
   - Create output directory structure
   - Generate safe filenames from issue keys and summaries
   - Write markdown files with UTF-8 encoding
   - Organize files by project/type/epic
   - Add metadata tracking

5. **Main Orchestration** - **TODO** (Optional - may be app responsibility)
   - Wire all modules together
   - Display progress indicators
   - Implement logging
   - Handle errors gracefully
   - **Note:** Since this is a library, orchestration may be the consuming application's responsibility

## Technology Stack

### Python Libraries - **UPDATED**
- **✅ jira** (3.10.5+) - Official Jira API client with API token auth support
- **✅ jira2markdown** (0.5.0+) - Convert Jira markup to markdown using parsing grammars
- **✅ pydantic** (2.0.0+) - Data validation and settings management
- **pyyaml** (6.0+) - YAML parsing (optional, for applications that want YAML config)
- **Development:**
  - **pytest** (8.0.0+) - Testing framework with markers for unit/integration tests
  - **pytest-cov** - Code coverage reporting
  - **pytest-mock** - Mocking utilities
  - **python-dotenv** - For tests and example applications

### Removed Dependencies
- ~~**pydantic-settings**~~ - Library doesn't load config from environment
- ~~**tqdm**~~ - Progress bars are application's responsibility

## Configuration Approach - **UPDATED**

**Library provides:** Plain Pydantic data models for validation
**Applications provide:** Configuration loading logic

### Example Application Usage

```python
# Application code (not in library)
import os
from dotenv import load_dotenv
from jira_local_sync.config import JiraSettings
from jira_local_sync.jira_client import JiraClient

# App loads environment
load_dotenv()

# App creates settings
settings = JiraSettings(
    jira_url=os.getenv("JIRA_URL"),
    jira_email=os.getenv("JIRA_EMAIL"),
    jira_api_token=os.getenv("JIRA_API_TOKEN")
)

# Use library
client = JiraClient(settings)
issues = client.search_issues("project = MYPROJ")
```

### **.env** (gitignored - for applications)
```
JIRA_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_api_token_here
```

## Output Directory Structure (File Manager - TODO)

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

## Markdown File Template - **IMPLEMENTED**

Each issue markdown file contains:
```markdown
# [PROJ-123] Issue Title

**Key:** PROJ-123
**Type:** Story
**Status:** In Progress
**Priority:** High
**Assignee:** John Doe
**Reporter:** Jane Smith
**Created:** 2025-01-15 10:30
**Updated:** 2025-01-20 14:45
**Labels:** `backend` `api` `urgent`

## Description

[Converted markdown content from Jira]

## Comments

### John Doe - 2025-01-16 10:30

Comment text here...

## Attachments

- [document.pdf](https://example.com/document.pdf) (512.0 KB)

---
*Exported from Jira: 2025-12-11*
```

## Implementation Steps

### ✅ Step 1: Project Setup - **COMPLETED**
- ✅ Create project directory structure with `uv`
- ✅ Set up `pyproject.toml` with dependencies
- ✅ Create `.env.example` template
- ✅ Initialize git repository

### ✅ Step 2: Configuration Module - **COMPLETED**
- ✅ Implement plain Pydantic BaseModel for settings
- ✅ Validate required settings
- ✅ Applications handle environment variable loading
- ✅ Unit tests (9 tests)

### ✅ Step 3: Jira Client Module - **COMPLETED**
- ✅ Implement API token authentication
- ✅ Create JQL query executor with pagination (100 results per page)
- ✅ Add methods to fetch:
  - ✅ Issue details with all fields
  - ✅ Comments and attachments metadata
  - ✅ Epic-story relationships (via `parent` link)
- ✅ Error handling for API failures
- ✅ Unit tests with mocking (15 tests)
- ✅ Integration tests with real Jira (10 tests)

### ✅ Step 4: Markdown Converter Module - **COMPLETED**
- ✅ Integrate jira2markdown library for text conversion
- ✅ Create issue metadata formatter
- ✅ Build template rendering for issues
- ✅ Handle special cases:
  - ✅ User mentions, issue links
  - ✅ Code blocks, tables, lists
  - ✅ Attachments (links/references)
- ✅ Unit tests (25 tests)
- ✅ Integration tests with real issues (5 tests)

### Step 5: File Manager Module - **TODO**
- Create directory structure based on configuration
- Generate safe filenames from issue keys and summaries
- Implement file writing with UTF-8 encoding
- Organize files by project/type/epic
- Add metadata.json export for tracking
- Unit tests
- Integration tests

### Step 6: Main Orchestration - **TODO** (Optional)
- Wire all modules together
- Add CLI with argparse (--config, --output-dir, --query)
- Implement progress tracking with tqdm
- Add comprehensive logging (INFO, DEBUG, ERROR levels)
- Create error handling for common failures
- **Note:** May be better as a separate application/example

### ✅ Step 7: Testing & Documentation - **IN PROGRESS**
- ✅ Comprehensive test suite with pytest
  - ✅ 64 total tests (49 unit, 15 integration)
  - ✅ Organized in `tests/unit/` and `tests/integration/`
  - ✅ Markers for unit/integration separation
  - ✅ 88% code coverage
- ✅ CLAUDE.md for development guidance
- ✅ .env.example template
- README with library usage instructions - **TODO**
- Document configuration options - **TODO**
- Add usage examples - **TODO**

## Key Considerations

### Jira API Specifics
- **Pagination:** ✅ Implemented - Jira REST API returns max 50-100 results per request, use `startAt` parameter
- **Rate Limiting:** Jira Cloud has rate limits (typically 10,000 requests/day) - TODO: implement backoff
- **Epic Links:** ✅ Handled - Epic-story relationships use `parent` field (v3 API)
- **Sprint Field:** Sprint data comes from Agile/Software API - TODO: if needed
- **Field Mapping:** ✅ Dynamic field handling - Jira fields vary by instance

### Error Handling
- ✅ Invalid credentials → Clear error messages with ValidationError
- ✅ Network failures → JIRAError exceptions with details
- ✅ Invalid JQL → Jira error message passed through
- Large exports → Stream to disk, show progress - TODO (file manager)

### Performance
- ✅ Fetch issues in batches (100 at a time with automatic pagination)
- Use concurrent requests for independent operations - TODO (optional optimization)
- Cache epic/sprint lookups to avoid redundant API calls - TODO (optional optimization)
- Provide progress indicators for long-running exports - TODO (application responsibility)

## Project Status

### Completed Modules
1. ✅ **config.py** - Plain Pydantic settings model
2. ✅ **jira_client.py** - Full Jira API integration
3. ✅ **markdown_converter.py** - Complete markdown conversion

### TODO Modules
4. **file_manager.py** - File organization and writing
5. **Main orchestration** (optional - may be example app)

### Test Coverage
- **64 tests total** (49 unit, 15 integration)
- **88% code coverage**
- Unit tests: Fast, no credentials needed
- Integration tests: Require `.env` with real Jira credentials

### Dependencies
```toml
dependencies = [
    "jira>=3.10.5",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",  # Optional for apps
    "jira2markdown>=0.5.0",
]

[dev]
    "pytest>=8.0.0",
    "pytest-cov>=6.0.0",
    "pytest-mock>=3.14.0",
    "python-dotenv>=1.0.0",  # For tests
```

## Next Steps

1. **Implement File Manager Module**
   - Directory structure creation
   - Safe filename generation
   - File writing with UTF-8
   - Metadata tracking

2. **Create Example Application** (optional)
   - Demonstrate library usage
   - Show configuration loading patterns
   - CLI interface with argparse
   - Progress tracking

3. **Documentation**
   - README with usage examples
   - API documentation
   - Configuration guide
   - Troubleshooting

4. **Additional Features** (optional)
   - Rate limiting/retry logic
   - Concurrent request optimization
   - More export formats
