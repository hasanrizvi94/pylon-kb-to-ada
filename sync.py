# Standard library imports for HTTP requests, logging, and date handling
import requests
from markdownify import markdownify as md  # Converts HTML content to Markdown format
import logging
from datetime import datetime

# Configure logging to write sync operations and errors to a file
# This helps track the sync process and debug any issues
logging.basicConfig(
    filename='sync.log',  # Log file name
    level=logging.INFO,   # Log level - captures INFO and above (WARNING, ERROR, CRITICAL)
    format='%(asctime)s [%(levelname)s] %(message)s'  # Include timestamp and log level
)

def get_user_credentials():
    """Prompt user for their API credentials and bot handle."""
    print("Welcome to the Pylon-to-Ada Knowledge Base Sync Tool!")
    print("Please provide the following information:\n")

    # Get bot handle (maps to Ada bot URL)
    bot_handle = input("Enter your Ada bot handle (e.g., 'my-bot' for my-bot.ada.support): ").strip()
    if not bot_handle:
        raise ValueError("Bot handle is required")

    # Get API keys
    ada_api_key = input("Enter your Ada API key: ").strip()
    if not ada_api_key:
        raise ValueError("Ada API key is required")

    pylon_api_key = input("Enter your Pylon API key: ").strip()
    if not pylon_api_key:
        raise ValueError("Pylon API key is required")

    # Construct Ada bot URL
    ada_bot_url = f"https://{bot_handle}.ada.support"

    print(f"\nConfiguration:")
    print(f"Ada Bot URL: {ada_bot_url}")
    print(f"Ada API Key: {ada_api_key[:10]}...")
    print(f"Pylon API Key: {pylon_api_key[:10]}...\n")

    return pylon_api_key, ada_api_key, ada_bot_url

def log_and_print(msg, bot_handle=None, source_id=None):
    # Add bot handle and source ID context to message
    if bot_handle and source_id:
        formatted_msg = f"[{bot_handle}:{source_id}] {msg}"
    elif bot_handle:
        formatted_msg = f"[{bot_handle}] {msg}"
    else:
        formatted_msg = msg

    print(formatted_msg)        # Display message to user in real-time
    logging.info(formatted_msg) # Write message to log file for permanent record

def get_pylon_kb(pylon_api_key, bot_handle=None):
    # Make authenticated GET request to fetch all knowledge bases
    res = requests.get(
        "https://api.usepylon.com/knowledge-bases",
        headers={
            "Authorization": f"Bearer {pylon_api_key}",  # Bearer token authentication
            "Content-Type": "application/json"           # Specify JSON content type
        }
    )

    # Raise exception if request failed (4xx or 5xx status codes)
    res.raise_for_status()

    # Extract the data array from JSON response
    data = res.json()["data"]

    # Get ID and title from the first knowledge base
    # Note: This assumes at least one knowledge base exists
    kb_id = data[0]["id"]
    kb_name = data[0]["title"]

    # Log the found knowledge base for tracking
    log_and_print(f"Found Pylon KB: {kb_name} (ID: {kb_id})", bot_handle)

    return kb_id, kb_name

def get_articles(kb_id, pylon_api_key, bot_handle=None, source_id=None):
    # Make authenticated GET request to fetch articles from specific knowledge base
    # Limit set to 200 to fetch more articles while avoiding overwhelming the API
    res = requests.get(
        f"https://api.usepylon.com/knowledge-bases/{kb_id}/articles?limit=200",
        headers={
            "Authorization": f"Bearer {pylon_api_key}",  # Bearer token authentication
            "Content-Type": "application/json"           # Specify JSON content type
        }
    )

    # Raise exception if request failed
    res.raise_for_status()

    # Extract articles array from JSON response
    articles = res.json()["data"]

    # Log the number of articles retrieved for tracking
    log_and_print(f"Retrieved {len(articles)} articles.", bot_handle, source_id)

    return articles

def create_ada_source(kb_id, kb_name, ada_api_key, ada_bot_url, bot_handle=None):
    # Prepare the payload for creating Ada knowledge source
    # Using the same ID ensures consistency between Pylon and Ada
    payload = {
        "id": kb_id,  # Must match Pylon KB ID for consistent mapping
        "name": f"Pylon ({kb_name or 'Untitled'})"  # Descriptive name with fallback
    }

    log_and_print(f"Creating Ada knowledge source with: {payload}", bot_handle)

    # Make authenticated POST request to create the knowledge source
    res = requests.post(
        f"{ada_bot_url}/api/v2/knowledge/sources",
        headers={
            "Authorization": f"Bearer {ada_api_key}",  # Bearer token authentication
            "Content-Type": "application/json"         # Specify JSON payload
        },
        json=payload  # Automatically serializes dict to JSON
    )

    # Handle potential API errors with detailed error information
    try:
        res.raise_for_status()  # Raises HTTPError for bad responses
    except Exception:
        # Print Ada's error response for debugging before re-raising
        print("Ada response:", res.text)
        raise

    # Extract the source ID from our payload (since Ada uses the ID we provided)
    source_id = payload["id"]
    log_and_print(f"Created Ada knowledge source: {source_id}", bot_handle, source_id)

    # Record the created source ID with timestamp for cleanup tracking
    # This file helps identify sources that can be deleted later
    with open("source_ids.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {bot_handle}:{source_id}\n")

    return source_id

def upsert_articles(articles, source_id, ada_api_key, ada_bot_url, bot_handle=None):
    formatted = []  # List to store Ada-formatted article objects

    # Process each Pylon article and convert to Ada format
    for article in articles:
        # Convert HTML content to Markdown using markdownify library
        # This makes the content more readable and compatible with Ada
        content = md(article.get("current_published_content_html", "") or "")

        # Skip articles with empty content (Ada requires non-empty content)
        if not content.strip():
            log_and_print(f"Skipping article '{article.get('title', 'Untitled')}' - empty content", bot_handle, source_id)
            continue

        # Extract the most recent update timestamp, with fallback options
        # Different Pylon sources may use different timestamp field names
        article_title = article.get("title") or article.get("name") or "Untitled"

        # Extract timestamp for article

        # Try various timestamp field names that might exist
        updated_at = (
            article.get("updated_at") or
            article.get("modified_at") or
            article.get("last_updated") or
            article.get("last_modified") or
            article.get("last_published_at") or  # This is the key field from Pylon!
            article.get("published_at") or
            article.get("date_updated") or
            article.get("date_modified")
        )

        # Log articles with missing timestamps to help identify data issues
        if not updated_at:
            log_and_print(f"Warning: Article '{article_title}' has no timestamp - using default date", bot_handle, source_id)
            updated_at = "2020-01-01T00:00:00Z"  # Use a default historical date instead of current time

        # Create Ada-compatible article object
        formatted.append({
            "id": article.get("id") or article.get("_id"),  # Handle different ID field names
            "name": article.get("title") or article.get("name") or "Untitled",  # Article title with fallback
            "content": content,  # Converted Markdown content
            "knowledge_source_id": source_id,  # Link to the Ada knowledge source
            "external_updated": updated_at  # Last modification timestamp
        })

    # Check if we have any articles to upload
    if not formatted:
        log_and_print("No articles with valid content found to upload.", bot_handle, source_id)
        return

    log_and_print(f"Uploading {len(formatted)} articles to Ada.", bot_handle, source_id)

    # Use Ada's bulk upload API to efficiently upload all articles at once
    # This is much faster than individual article uploads
    res = requests.post(
        f"{ada_bot_url}/api/v2/knowledge/bulk/articles/",
        headers={
            "Authorization": f"Bearer {ada_api_key}",  # Bearer token authentication
            "Content-Type": "application/json"         # Specify JSON payload
        },
        json=formatted  # Send the formatted articles array
    )

    # Handle potential API errors with detailed error information
    try:
        res.raise_for_status()  # Raises HTTPError for bad responses
    except Exception:
        # Print Ada's error response for debugging before re-raising
        print("Ada response:", res.text)
        raise

    log_and_print(f"Uploaded {len(formatted)} articles to Ada.", bot_handle, source_id)

# Main execution block - only runs when script is executed directly (not imported)
if __name__ == "__main__":
    try:
        # Step 0: Get user credentials and configuration
        pylon_api_key, ada_api_key, ada_bot_url = get_user_credentials()

        # Extract bot handle from URL
        bot_handle = ada_bot_url.replace("https://", "").replace(".ada.support", "")

        # Step 1: Get the Pylon knowledge base information
        # This identifies which knowledge base to sync from
        kb_id, kb_name = get_pylon_kb(pylon_api_key, bot_handle)

        # Step 2: Retrieve all articles from the Pylon knowledge base
        # This fetches the actual content that needs to be synced
        articles = get_articles(kb_id, pylon_api_key, bot_handle)

        # Step 3: Create a corresponding knowledge source in Ada
        # This creates the container where Pylon articles will be stored
        ada_source_id = create_ada_source(kb_id, kb_name, ada_api_key, ada_bot_url, bot_handle)

        # Step 4: Convert and upload all articles to Ada
        # This performs the actual content migration
        upsert_articles(articles, ada_source_id, ada_api_key, ada_bot_url, bot_handle)

        # Log successful completion
        log_and_print("Sync completed successfully.", bot_handle, ada_source_id)

        # Provide cleanup instructions for the user
        # The delete.py script can be used to remove the created source if needed
        log_and_print(f"To delete this source, run: python delete.py {ada_source_id} {ada_bot_url} {ada_api_key}", bot_handle, ada_source_id)

    except Exception as e:
        # Handle any errors that occur during the sync process
        # Log the error to file and display to user
        logging.error(f"Sync failed: {e}")
        print(f"Error: {e}")