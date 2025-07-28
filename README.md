# Pylon KB to Ada Knowledge Base Sync

A Python tool to synchronize knowledge base articles from Pylon to Ada Support's knowledge management system.

## Overview

This tool provides a proof-of-concept implementation for migrating knowledge base content from Pylon to Ada Support. It fetches articles from Pylon's API, converts HTML content to Markdown, and uploads them to Ada's knowledge base system.

## Features

- **Sync Articles**: Fetches all articles from a Pylon knowledge base and uploads them to Ada
- **Content Conversion**: Automatically converts HTML content to Markdown format
- **Logging**: Comprehensive logging to `sync.log` for troubleshooting
- **Source Tracking**: Maintains a record of created knowledge sources in `source_ids.txt`
- **Cleanup Utility**: Includes a deletion script to remove synchronized sources

## Files

- `sync.py` - Main synchronization script
- `delete.py` - Utility to delete Ada knowledge sources
- `source_ids.txt` - Log of created source IDs with timestamps
- `sync.log` - Detailed operation logs

## Dependencies

- `requests` - HTTP client for API calls
- `markdownify` - HTML to Markdown conversion

## Setup

1. Install required dependencies:
   ```bash
   pip install requests markdownify
   ```

2. Configure API keys in the scripts:
   - Update `PYLON_API_KEY` in `sync.py`
   - Update `ADA_API_KEY` in both `sync.py` and `delete.py`

## Usage

### Sync Knowledge Base
```bash
python sync.py
```

This will:
1. Fetch the first knowledge base from Pylon
2. Retrieve all articles (up to 50)
3. Create a corresponding knowledge source in Ada
4. Upload all articles with converted Markdown content

### Delete Knowledge Source
```bash
python delete.py <SOURCE_ID>
```

Replace `<SOURCE_ID>` with the ID of the Ada knowledge source to delete.

## API Endpoints

- **Pylon**: `https://api.usepylon.com/knowledge-bases`
- **Ada**: `https://hasan-test-gr.ada.support/api/v2/knowledge/`

## Logging

All operations are logged to `sync.log` with timestamps and detailed information about:
- API requests and responses
- Article processing
- Success/failure status
- Error details

## Notes

- Currently configured for test environment (`hasan-test-gr.ada.support`)
- Processes up to 50 articles per sync (Pylon API limit)
- Maintains article IDs and timestamps for synchronization tracking
