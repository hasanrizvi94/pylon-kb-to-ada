# Pylon KB to Ada Knowledge Base Sync

A Python tool to synchronize knowledge base articles from Pylon to Ada Support's knowledge management system.

## Overview

This tool provides a production-ready implementation for migrating knowledge base content from Pylon to Ada Support. It features a modular architecture with separated API clients, secure configuration management, and comprehensive error handling.

## Features

- **Sync Articles**: Fetches all articles from a Pylon knowledge base and uploads them to Ada
- **Content Conversion**: Automatically converts HTML content to Markdown format
- **Secure Configuration**: Environment variables and YAML-based configuration
- **Modular Architecture**: Separated API clients and business logic
- **Comprehensive Logging**: Detailed logging with configurable output
- **Source Tracking**: Maintains a record of created knowledge sources with timestamps
- **Cleanup Utility**: Includes a deletion script to remove synchronized sources

## Project Structure

```
pylon-kb-to-ada/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── pylon_client.py    # Pylon API client
│   ├── ada_client.py      # Ada API client
│   └── sync_manager.py    # Business logic
├── scripts/
│   ├── sync.py           # Main synchronization script
│   └── delete.py         # Deletion utility script
├── tests/                # Test directory (ready for unit tests)
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── config.yaml.example # Configuration file template
└── .gitignore          # Git ignore rules
```

## Dependencies

Install from `requirements.txt`:
- `requests==2.31.0` - HTTP client for API calls
- `markdownify==0.11.6` - HTML to Markdown conversion
- `python-dotenv==1.0.0` - Environment variable loading
- `pyyaml==6.0.1` - YAML configuration support

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys** (choose one method):

   **Option A: Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   **Option B: Configuration File**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your settings
   ```

3. **Required Configuration:**
   - `PYLON_API_KEY` - Your Pylon API key
   - `ADA_API_KEY` - Your Ada API key
   - `ADA_BASE_URL` - Your Ada instance URL (e.g., `https://your-instance.ada.support`)

## Usage

### Sync Knowledge Base
```bash
python scripts/sync.py
```

This will:
1. Fetch the first knowledge base from Pylon
2. Retrieve all articles (configurable limit, default 50)
3. Create a corresponding knowledge source in Ada
4. Upload all articles with converted Markdown content
5. Log the source ID for future reference

### Delete Knowledge Source
```bash
python scripts/delete.py <SOURCE_ID>
```

Replace `<SOURCE_ID>` with the ID of the Ada knowledge source to delete.

## Configuration Options

### Environment Variables
- `PYLON_API_KEY` - Pylon API authentication key
- `ADA_API_KEY` - Ada API authentication key
- `PYLON_BASE_URL` - Pylon API base URL (default: `https://api.usepylon.com`)
- `ADA_BASE_URL` - Ada API base URL
- `ARTICLE_LIMIT` - Maximum articles to sync (default: 50)
- `LOG_FILE` - Log file path (default: `sync.log`)
- `SOURCE_IDS_FILE` - Source IDs tracking file (default: `source_ids.txt`)

### Configuration File
See `config.yaml.example` for YAML-based configuration options.

## API Endpoints

- **Pylon**: `https://api.usepylon.com/knowledge-bases`
- **Ada**: `{ADA_BASE_URL}/api/v2/knowledge/`

## Logging

All operations are logged with timestamps and detailed information about:
- API requests and responses
- Article processing status
- Success/failure notifications
- Error details and stack traces

Log files are automatically created and can be configured via environment variables or config file.

## Security

- API keys are never stored in source code
- Sensitive configuration files are excluded from version control
- Environment variables take precedence over configuration files
- Comprehensive `.gitignore` prevents accidental key exposure

## Development

### Running Tests
```bash
# Tests directory is ready for unit tests
python -m pytest tests/
```

### Project Structure
- `src/` - Core library modules
- `scripts/` - Command-line entry points
- `tests/` - Unit tests (to be implemented)
- Configuration files use templates to prevent key exposure
