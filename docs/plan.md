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

4. **✅ Processor Module** (`processor.py`) - **COMPLETED**
   - High-level orchestration layer for the library
   - Memory-efficient generator pattern for processing issues
   - Configurable options for comments and attachments
   - **Implementation:**
     - `JiraProcessor` class combining client and converter
     - `process_issues()` generator yielding (issue_key, markdown) tuples
     - `process_single_issue()` for individual issue processing
     - `test_connection()` for validating Jira credentials

5. **File Manager Module** (`file_manager.py`) - **ADDITIONAL FEATURE**
   - Create output directory structure
   - Generate safe filenames from issue keys and summaries
   - Write markdown files with UTF-8 encoding
   - Organize files by project/type/epic
   - Add metadata tracking
   - **Note:** File management is typically the consuming application's responsibility

## Technology Stack

### Python Libraries - **UPDATED**
- **✅ jira** (3.10.5+) - Official Jira API client with API token auth support
- **✅ jira2markdown** (0.5.0+) - Convert Jira markup to markdown using parsing grammars
- **✅ pydantic** (2.0.0+) - Data validation and settings management
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
from jira_local_sync import JiraSettings, JiraProcessor

# App loads environment
load_dotenv()

# App creates settings
settings = JiraSettings(
    jira_url=os.getenv("JIRA_URL"),
    jira_email=os.getenv("JIRA_EMAIL"),
    jira_api_token=os.getenv("JIRA_API_TOKEN")
)

# Use library processor
processor = JiraProcessor(settings)

# Process issues using generator pattern
for issue_key, markdown_content in processor.process_issues("project = MYPROJ"):
    print(f"Processing {issue_key}...")
    # Application handles file writing
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

### ✅ Step 5: Processor Module - **COMPLETED**
- ✅ Create `JiraProcessor` class combining client and converter
- ✅ Implement `process_issues()` generator for memory-efficient processing
- ✅ Implement `process_single_issue()` for individual issue handling
- ✅ Add configurable options (include_comments, include_attachments)
- ✅ Error handling for failed conversions
- ✅ Unit tests (12 tests)
- ✅ Integration tests with real Jira (9 tests)

### Step 6: File Manager Module - **ADDITIONAL FEATURE**
- Create directory structure based on configuration
- Generate safe filenames from issue keys and summaries
- Implement file writing with UTF-8 encoding
- Organize files by project/type/epic
- Add metadata.json export for tracking
- **Note:** This is an optional feature - applications can handle file management themselves

### Step 7: Example Application - **OPTIONAL**
- Demonstrate library usage patterns
- Show configuration loading from environment
- CLI interface with argparse (--config, --output-dir, --query)
- Implement progress tracking with tqdm
- Add comprehensive logging (INFO, DEBUG, ERROR levels)
- File writing and organization
- **Note:** This would be a separate application, not part of the library

### ✅ Step 8: Testing & Documentation - **IN PROGRESS**
- ✅ Comprehensive test suite with pytest
  - ✅ 85 total tests (61 unit, 24 integration)
  - ✅ Organized in `tests/unit/` and `tests/integration/`
  - ✅ Markers for unit/integration separation
  - ✅ High code coverage across all modules
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
4. ✅ **processor.py** - High-level orchestration with generator pattern

### Optional/Future Modules
5. **file_manager.py** - File organization and writing (application responsibility)
6. **Example application** - CLI tool demonstrating library usage

### Test Coverage
- **85 tests total** (61 unit, 24 integration)
- **High code coverage** across all modules
- Unit tests: Fast (< 1 second), no credentials needed
- Integration tests: Comprehensive (~35 seconds), require `.env` with real Jira credentials
- Test organization: `tests/unit/` and `tests/integration/` with pytest markers

### Dependencies
```toml
dependencies = [
    "jira>=3.10.5",
    "pydantic>=2.0.0",
    "jira2markdown>=0.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=6.0.0",
    "pytest-mock>=3.14.0",
    "python-dotenv>=1.0.0",  # For tests and example apps
]
```

## Next Steps

1. **Documentation** (Priority)
   - README with library usage examples
   - API documentation for all public classes
   - Configuration guide
   - Troubleshooting section

2. **Create Example Application** (Recommended)
   - Demonstrate library usage patterns
   - Show configuration loading from environment
   - CLI interface with argparse
   - File writing and organization
   - Progress tracking with tqdm

3. **Optional Enhancements**
   - Rate limiting/retry logic for API calls
   - Concurrent request optimization
   - Additional export formats (JSON, HTML)
   - File manager module (if needed as part of library)
