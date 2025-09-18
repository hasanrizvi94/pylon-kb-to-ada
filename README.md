# Pylon KB to Ada Knowledge Base Sync

A Python tool to synchronize knowledge base articles from Pylon to Ada Support's knowledge management system. Works with any Ada bot instance and Pylon account through interactive credential prompts.

## Overview

This tool provides a comprehensive solution for migrating and maintaining knowledge base content from Pylon to Ada Support. It includes both initial sync capabilities and intelligent delta synchronization to keep your knowledge bases up-to-date.

## Features

- **Universal Compatibility**: Works with any Ada bot and Pylon account through interactive prompts
- **Secure Credential Handling**: Prompts for API keys and bot handles at runtime (no hardcoded credentials)
- **Initial Sync**: Fetches all articles from a Pylon knowledge base and uploads them to Ada
- **Delta Sync**: Intelligent synchronization that only updates changed articles
- **Timestamp-Based Sync**: Uses `last_published_at` timestamps for accurate change detection
- **Content Conversion**: Automatically converts HTML content to Markdown format
- **Smart Filtering**: Skips articles with empty content to ensure Ada API compliance
- **Comprehensive Logging**: Detailed logging for both sync operations and troubleshooting
- **Source Tracking**: Maintains a record of created knowledge sources in `source_ids.txt`
- **Cleanup Utility**: Includes a deletion script to remove synchronized sources

## Files

- `sync.py` - Initial synchronization script (creates new knowledge source)
- `update_sync.py` - Delta synchronization script (updates existing knowledge source)
- `delete.py` - Utility to delete Ada knowledge sources
- `source_ids.txt` - Log of created source IDs with timestamps
- `sync.log` - Detailed operation logs for initial sync
- `update_sync.log` - Detailed operation logs for delta sync

## Dependencies

Install required dependencies:
```bash
pip install requests markdownify python-dateutil
```

Required packages:
- `requests` - HTTP client for API calls
- `markdownify` - HTML to Markdown conversion
- `python-dateutil` - Timezone-aware timestamp parsing

## Setup

**No configuration needed!** The scripts will prompt you for:
- Your Ada bot handle (e.g., "my-bot" for my-bot.ada.support)
- Your Pylon API key
- Your Ada API key

## Usage

### Initial Knowledge Base Sync

For first-time migration or creating a new knowledge source:

```bash
python sync.py
```

The script will prompt you for:
1. **Ada bot handle**: Enter your bot subdomain (e.g., "my-company" for my-company.ada.support)
2. **Ada API key**: Your Ada API authentication key
3. **Pylon API key**: Your Pylon API authentication key
4. **Pylon knowledge base ID**: The ID of the specific knowledge base to sync

Then it will:
1. Validate the knowledge base exists and fetch its details
2. Retrieve all articles (up to 200) from the specified KB
3. Create a corresponding knowledge source in Ada
4. Upload all articles with converted Markdown content
5. Log the new source ID for future delta syncs

### Delta Sync (Recommended for Updates)

For ongoing synchronization of an existing knowledge source:

```bash
python update_sync.py
```

The script will prompt you for:
1. **Ada bot handle**: Your bot subdomain
2. **Ada API key**: Your Ada API authentication key
3. **Pylon API key**: Your Pylon API authentication key
4. **Pylon knowledge base ID**: The ID of your Pylon knowledge base
5. **Ada knowledge source ID**: The ID of your Ada knowledge source (from initial sync)

The delta sync will:
1. **Compare timestamps**: Uses `last_published_at` from Pylon vs Ada
2. **Create new articles**: Articles in Pylon but not in Ada
3. **Update changed articles**: Articles where Pylon timestamp > Ada timestamp
4. **Delete removed articles**: Articles in Ada but no longer in Pylon
5. **Skip unchanged articles**: Articles with matching timestamps

**Delta Sync Output:**
```
Articles to create: 0
Article unchanged: 'Adding a New User to Your Account' - timestamps match
Article unchanged: 'How to Submit a Feature Request' - timestamps match
Articles to update: 0
Articles to delete: 0
Delta sync completed: 0 created, 0 updated, 0 deleted
```

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

Replace the placeholders with your actual values. The sync scripts provide the exact delete command at completion.

## Sync Strategy

### When to Use Each Script

- **`sync.py`**: Use for initial migration or creating new knowledge sources from any Pylon KB
- **`update_sync.py`**: Use for ongoing maintenance and updates of existing sources

### Multiple Knowledge Bases Support

Both scripts now support multiple knowledge bases within the same Pylon account:

- **Automatic KB selection**: Enter the specific KB ID you want to sync
- **Multi-KB workflows**: Sync different Pylon KBs to separate Ada knowledge sources
- **Enterprise ready**: Perfect for organizations with multiple product lines or teams

### Timestamp-Based Synchronization

The delta sync uses Pylon's `last_published_at` field to determine when articles were last modified:

- **Pylon format**: `2025-07-11T19:20:22Z`
- **Ada format**: `2025-07-11T19:20:22+00:00`
- **Smart comparison**: Handles timezone format differences automatically
- **Accurate detection**: Only articles with newer Pylon timestamps are updated

### Content Hash Fallback

If timestamp parsing fails, the system falls back to content hash comparison for reliability.

## API Endpoints

- **Pylon**:
  - Knowledge bases: `https://api.usepylon.com/knowledge-bases`
  - Articles: `https://api.usepylon.com/knowledge-bases/{kb_id}/articles`
  - Single article: `https://api.usepylon.com/knowledge-bases/{kb_id}/articles/{id}`
- **Ada**:
  - Create knowledge source: `https://{bot-url}.ada.support/api/v2/knowledge/sources`
  - Bulk upload articles: `https://{bot-url}.ada.support/api/v2/knowledge/bulk/articles/`
  - Get articles: `https://{bot-url}.ada.support/api/v2/knowledge/articles/`
  - Delete articles: `https://{bot-url}.ada.support/api/v2/knowledge/articles/`
  - Delete knowledge source: `https://{bot-url}.ada.support/api/v2/knowledge/sources/{source_id}`

## Rate Limits

- **Pylon**:
  - GET `/articles`: 60 req/min
  - GET `/articles/{id}`: 20 req/min

## Logging

### Initial Sync Logging (`sync.log`)
- API requests and responses
- Article processing with timestamp detection
- Success/failure status
- Error details

### Delta Sync Logging (`update_sync.log`)
- Detailed comparison results
- Timestamp matching/differences
- Create/Update/Delete operations
- Performance metrics

### Clean Terminal Output
Both scripts provide clean terminal output without verbose API payloads:
```
Starting delta sync...
Retrieved 6 articles from Pylon
Retrieved 6 articles from Ada
Articles to create: 0
Article unchanged: 'Adding a New User to Your Account' - timestamps match
Articles to update: 0
Articles to delete: 0
Delta sync completed: 0 created, 0 updated, 0 deleted
```

## Security

- **No hardcoded credentials**: All API keys and bot URLs are entered at runtime
- **Git history cleaned**: No sensitive information stored in repository history
- **Safe for public repositories**: Anyone can use this tool with their own credentials

## Troubleshooting

### Common Issues

1. **Missing timestamps**: Articles without `last_published_at` use fallback date `2020-01-01T00:00:00Z`
2. **Timezone differences**: Automatically handled by `python-dateutil`
3. **Content hash mismatches**: Normal due to HTML/Markdown conversion differences
4. **Empty articles**: Automatically skipped to prevent API errors

### Best Practices

1. **Use delta sync** for ongoing maintenance
2. **Monitor logs** for any timestamp parsing issues
3. **Test with small batches** before full migration
4. **Keep source IDs** from `source_ids.txt` for cleanup

## Notes

- **Universal compatibility**: Works with any Ada bot subdomain and Pylon account
- **Multiple KB support**: Sync any specific knowledge base by entering its ID
- **Consistent user experience**: Both scripts follow the same prompt sequence (Ada → Pylon)
- **Automatic URL construction**: Bot handle automatically constructs the full Ada API URL
- **Smart content filtering**: Skips articles with empty content to prevent API errors
- **Efficient sync**: Delta sync only processes changed articles
- **Timezone aware**: Handles different timestamp formats between Pylon and Ada
- **Clean codebase**: Removed all redundant/commented code for better maintainability
- Processes up to 200 articles per sync (Pylon API limit)
- Maintains article IDs and timestamps for accurate synchronization tracking

## Example Multi-KB Usage

**Scenario**: Company with separate KBs for different products

```bash
# Sync Product A KB to Ada
python sync.py
# Enter: ada-bot, ada-key, pylon-key, product-a-kb-id

# Sync Product B KB to Ada
python sync.py
# Enter: ada-bot, ada-key, pylon-key, product-b-kb-id

# Later, update both with delta sync
python update_sync.py
# Enter: ada-bot, ada-key, pylon-key, product-a-kb-id, product-a-source-id

python update_sync.py
# Enter: ada-bot, ada-key, pylon-key, product-b-kb-id, product-b-source-id
```

This creates separate knowledge sources in Ada for each Pylon KB, allowing independent management and updates.