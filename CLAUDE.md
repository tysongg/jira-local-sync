# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`jira-local-sync` is a Python package built with Python 3.14+ using the `uv` build system. This is a new project in early development with minimal implementation currently in place.

## Python Environment

- **Python Version**: 3.14 (specified in `.python-version`)
- **Package Manager**: Uses `uv` for dependency management and builds
- **Build Backend**: `uv_build` (version 0.9.8 - 0.10.0)

## Development Commands

### Package Management
```bash
# Install dependencies
uv sync

# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>
```

### Running Code
```bash
# Run Python code using the uv environment
uv run python -c "from jira_local_sync import hello; print(hello())"
```

### Building
```bash
# Build the package
uv build
```

## Project Structure

- `src/jira_local_sync/`: Main package source code
  - `__init__.py`: Package entry point with public API
  - `py.typed`: Marker file indicating the package supports type checking
- `pyproject.toml`: Project configuration, dependencies, and build settings

## Type Checking

This package includes `py.typed`, indicating it provides type hints. When adding new code, ensure proper type annotations are included following Python typing standards.

## Testing

This project uses pytest with markers to differentiate between unit and integration tests.

### Test Markers

- `@pytest.mark.unit` - Unit tests that use mocking and don't require external services
- `@pytest.mark.integration` - Integration tests that require real Jira credentials and network access

### Running Tests

```bash
# Run all tests (unit + integration, requires .env file)
uv run pytest

# Run only unit tests (fast, no credentials needed)
uv run pytest -m unit

# Run only integration tests (requires .env file)
uv run pytest -m integration

# Run specific test file
uv run pytest tests/test_config.py

# Run with verbose output
uv run pytest -v

# Run without coverage report
uv run pytest --no-cov
```

### Unit Tests

Unit tests use mocking and don't require external dependencies. They run quickly and can be executed without any configuration.

```bash
# Run all unit tests
uv run pytest -m unit
```

### Integration Tests

Integration tests verify the Jira client works with a real Jira instance. They require valid credentials.

**Prerequisites**: Create a `.env` file with your Jira credentials (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Run integration tests**:
```bash
uv run pytest -m integration
```

Integration tests will:
- Automatically skip if credentials are not configured
- Test connection to your Jira instance
- Search for issues using JQL
- Fetch individual issues and comments
- Verify pagination works correctly
