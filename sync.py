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

# API credentials for accessing Pylon and Ada services
# NOTE: In production, these should be stored as environment variables for security
PYLON_API_KEY = "YOUR_PYLON_API_KEY"
ADA_API_KEY = "***REMOVED***"

def log_and_print(msg):
    print(msg)        # Display message to user in real-time
    logging.info(msg) # Write message to log file for permanent record

def get_pylon_kb():
    # Make authenticated GET request to fetch all knowledge bases
    res = requests.get(
        "https://api.usepylon.com/knowledge-bases",
        headers={
            "Authorization": f"Bearer {PYLON_API_KEY}",  # Bearer token authentication
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
    log_and_print(f"Found Pylon KB: {kb_name} (ID: {kb_id})")
    
    return kb_id, kb_name

def get_articles(kb_id):
    # Make authenticated GET request to fetch articles from specific knowledge base
    # Limit set to 200 to fetch more articles while avoiding overwhelming the API
    res = requests.get(
        f"https://api.usepylon.com/knowledge-bases/{kb_id}/articles?limit=200",
        headers={
            "Authorization": f"Bearer {PYLON_API_KEY}",  # Bearer token authentication
            "Content-Type": "application/json"           # Specify JSON content type
        }
    )
    
    # Raise exception if request failed
    res.raise_for_status()
    
    # Extract articles array from JSON response
    articles = res.json()["data"]
    
    # Log the number of articles retrieved for tracking
    log_and_print(f"Retrieved {len(articles)} articles.")
    
    return articles

def create_ada_source(kb_id, kb_name):
    # Prepare the payload for creating Ada knowledge source
    # Using the same ID ensures consistency between Pylon and Ada
    payload = {
        "id": kb_id,  # Must match Pylon KB ID for consistent mapping
        "name": f"Pylon ({kb_name or 'Untitled'})"  # Descriptive name with fallback
    }

    log_and_print(f"Creating Ada knowledge source with: {payload}")

    # Make authenticated POST request to create the knowledge source
    res = requests.post(
        "https://hasan-gen-test.ada.support/api/v2/knowledge/sources",
        headers={
            "Authorization": f"Bearer {ADA_API_KEY}",  # Bearer token authentication
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
    log_and_print(f"Created Ada knowledge source: {source_id}")

    # Record the created source ID with timestamp for cleanup tracking
    # This file helps identify sources that can be deleted later
    with open("source_ids.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {source_id}\n")

    return source_id

def upsert_articles(articles, source_id):
    formatted = []  # List to store Ada-formatted article objects

    # Process each Pylon article and convert to Ada format
    for article in articles:
        # Convert HTML content to Markdown using markdownify library
        # This makes the content more readable and compatible with Ada
        content = md(article.get("current_published_content_html", "") or "")
        
        # Extract the most recent update timestamp, with fallback options
        # Different Pylon sources may use different timestamp field names
        updated_at = (
            article.get("updated_at")     # Primary timestamp field
            or article.get("modified_at") # Alternative timestamp field
            or datetime.utcnow().isoformat() + "Z"  # Fallback to current time in ISO format
        )

        # Create Ada-compatible article object
        formatted.append({
            "id": article.get("id") or article.get("_id"),  # Handle different ID field names
            "name": article.get("title") or article.get("name") or "Untitled",  # Article title with fallback
            "content": content,  # Converted Markdown content
            "knowledge_source_id": source_id,  # Link to the Ada knowledge source
            "external_updated": updated_at  # Last modification timestamp
        })

    log_and_print(f"Uploading {len(formatted)} articles to Ada.")

    # Use Ada's bulk upload API to efficiently upload all articles at once
    # This is much faster than individual article uploads
    res = requests.post(
        "https://hasan-gen-test.ada.support/api/v2/knowledge/bulk/articles/",
        headers={
            "Authorization": f"Bearer {ADA_API_KEY}",  # Bearer token authentication
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

    log_and_print(f"Uploaded {len(formatted)} articles to Ada.")

# Main execution block - only runs when script is executed directly (not imported)
if __name__ == "__main__":
    try:
        # Step 1: Get the Pylon knowledge base information
        # This identifies which knowledge base to sync from
        kb_id, kb_name = get_pylon_kb()
        
        # Step 2: Retrieve all articles from the Pylon knowledge base
        # This fetches the actual content that needs to be synced
        articles = get_articles(kb_id)
        
        # Step 3: Create a corresponding knowledge source in Ada
        # This creates the container where Pylon articles will be stored
        ada_source_id = create_ada_source(kb_id, kb_name)
        
        # Step 4: Convert and upload all articles to Ada
        # This performs the actual content migration
        upsert_articles(articles, ada_source_id)
        
        # Log successful completion
        log_and_print("Sync completed successfully.")
        
        # Provide cleanup instructions for the user
        # The delete.py script can be used to remove the created source if needed
        log_and_print(f"To delete this source, run: python delete.py {ada_source_id}")
        
    except Exception as e:
        # Handle any errors that occur during the sync process
        # Log the error to file and display to user
        logging.error(f"Sync failed: {e}")
        print(f"Error: {e}")