#!/usr/bin/env python3
"""Example application that fetches all stories from the Calypso (CAL) project.

This example demonstrates:
1. Creating settings from environment variables
2. Fetching all stories from a specific Jira project
3. Saving each issue as a markdown file in the ./output/ directory

Usage:
    # Make sure your environment variables are set (or use a .env file)
    export JIRA_URL="https://yourcompany.atlassian.net"
    export JIRA_EMAIL="your.email@company.com"
    export JIRA_API_TOKEN="your_api_token_here"
    
    # Run the example
    python examples/calypso_stories.py
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to allow importing from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.jira_local_sync import JiraSettings, JiraProcessor


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_settings_from_env() -> JiraSettings:
    """Load Jira settings from environment variables.
    
    Returns:
        JiraSettings instance with values from environment
        
    Raises:
        ValueError: If required environment variables are not set
    """
    jira_url = os.environ.get('JIRA_URL')
    jira_email = os.environ.get('JIRA_EMAIL')
    jira_api_token = os.environ.get('JIRA_API_TOKEN')
    
    # Check for missing environment variables
    missing = []
    if not jira_url:
        missing.append('JIRA_URL')
    if not jira_email:
        missing.append('JIRA_EMAIL')
    if not jira_api_token:
        missing.append('JIRA_API_TOKEN')
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please set these environment variables or create a .env file.\n"
            "See .env.example for reference."
        )
    
    return JiraSettings(
        jira_url=jira_url,
        jira_email=jira_email,
        jira_api_token=jira_api_token,
    )


def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Calypso Stories export")
    
    try:
        # 1. Load settings from environment variables
        logger.info("Loading settings from environment variables...")
        settings = load_settings_from_env()
        logger.info(f"Connected to: {settings.jira_url}")
        
        # 2. Initialize the processor with comments and attachments enabled
        logger.info("Initializing Jira processor...")
        processor = JiraProcessor(
            settings=settings,
            include_comments=True,
            include_attachments=True,
        )
        
        # 3. Create output directory if it doesn't exist
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)
        logger.info(f"Output directory: {output_dir.absolute()}")
        
        # 4. Fetch all stories from CAL project
        jql = "project = CAL AND type = Story ORDER BY key ASC"
        logger.info(f"Fetching stories with JQL: {jql}")
        
        # 5. Process and save each issue
        issue_count = 0
        error_count = 0
        
        for issue_key, markdown_content in processor.process_issues(jql):
            try:
                # Save to markdown file
                output_file = output_dir / f"{issue_key}.md"
                output_file.write_text(markdown_content, encoding='utf-8')
                
                issue_count += 1
                logger.info(f"✓ Saved {issue_key} to {output_file}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"✗ Failed to save {issue_key}: {e}")
        
        # Summary
        logger.info("=" * 60)
        logger.info(f"Export complete!")
        logger.info(f"  Successfully saved: {issue_count} issues")
        if error_count > 0:
            logger.warning(f"  Failed to save: {error_count} issues")
        logger.info(f"  Output directory: {output_dir.absolute()}")
        logger.info("=" * 60)
        
        # Exit with error code if there were failures
        if error_count > 0:
            sys.exit(1)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
