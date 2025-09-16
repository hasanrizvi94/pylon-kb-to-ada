# Pylon KB to Ada Knowledge Base Sync

A Python tool to synchronize knowledge base articles from Pylon to Ada Support's knowledge management system. Works with any Ada bot instance and Pylon account through interactive credential prompts.

## Overview

This tool provides a proof-of-concept implementation for migrating knowledge base content from Pylon to Ada Support. It fetches articles from Pylon's API, converts HTML content to Markdown, and uploads them to Ada's knowledge base system.

## Features

- **Universal Compatibility**: Works with any Ada bot and Pylon account through interactive prompts
- **Secure Credential Handling**: Prompts for API keys and bot handles at runtime (no hardcoded credentials)
- **Sync Articles**: Fetches all articles from a Pylon knowledge base and uploads them to Ada
- **Content Conversion**: Automatically converts HTML content to Markdown format
- **Smart Filtering**: Skips articles with empty content to ensure Ada API compliance
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

2. **No configuration needed!** The scripts will prompt you for:
   - Your Ada bot handle (e.g., "my-bot" for my-bot.ada.support)
   - Your Pylon API key
   - Your Ada API key

## Usage

### Sync Knowledge Base
```bash
python sync.py
```

The script will prompt you for:
1. **Ada bot handle**: Enter your bot subdomain (e.g., "my-company" for my-company.ada.support)
2. **Pylon API key**: Your Pylon API authentication key
3. **Ada API key**: Your Ada API authentication key

Then it will:
1. Fetch the first knowledge base from Pylon
2. Retrieve all articles (up to 200)
3. Create a corresponding knowledge source in Ada
4. Upload all articles with converted Markdown content (skips articles with empty content)

### Delete Knowledge Source

**Option 1 - Interactive (Recommended):**
```bash
python delete.py <SOURCE_ID>
```
You'll be prompted for your Ada bot handle and API key.

**Option 2 - Direct:**
```bash
python delete.py <SOURCE_ID> <ADA_BOT_URL> <ADA_API_KEY>
```

Replace the placeholders with your actual values. The sync script provides the exact delete command at completion.

## API Endpoints

- **Pylon**: 
  - Knowledge bases: `https://api.usepylon.com/knowledge-bases`
  - Articles: `https://api.usepylon.com/knowledge-bases/{kb_id}/articles`
  - Single article: `https://api.usepylon.com/knowledge-bases/{kb_id}/articles/{id}`
- **Ada**: 
  - Create knowledge source: `https://{bot-url}.ada.support/api/v2/knowledge/sources`
  - Bulk upload articles: `https://{bot-url}.ada.support/api/v2/knowledge/bulk/articles/`
  - Delete knowledge source: `https://{bot-url}.ada.support/api/v2/knowledge/sources/{source_id}`

## Rate Limits

- **Pylon**:
  - GET `/articles`: 60 req/min
  - GET `/articles/{id}`: 20 req/min

## Logging

All operations are logged to `sync.log` with timestamps and detailed information about:
- API requests and responses
- Article processing
- Success/failure status
- Error details

## Security

- **No hardcoded credentials**: All API keys and bot URLs are entered at runtime
- **Git history cleaned**: No sensitive information stored in repository history
- **Safe for public repositories**: Anyone can use this tool with their own credentials

## Notes

- **Universal compatibility**: Works with any Ada bot subdomain and Pylon account
- **Automatic URL construction**: Bot handle automatically constructs the full Ada API URL
- **Smart content filtering**: Skips articles with empty content to prevent API errors
- Processes up to 200 articles per sync (Pylon API limit)
- Maintains article IDs and timestamps for synchronization tracking
