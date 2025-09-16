import requests
import sys

def get_deletion_credentials():
    """Prompt user for their API credentials and bot handle for deletion."""
    print("Ada Knowledge Source Deletion Tool")
    print("Please provide your Ada credentials:\n")

    # Get bot handle (maps to Ada bot URL)
    bot_handle = input("Enter your Ada bot handle (e.g., 'my-bot' for my-bot.ada.support): ").strip()
    if not bot_handle:
        raise ValueError("Bot handle is required")

    # Get Ada API key
    ada_api_key = input("Enter your Ada API key: ").strip()
    if not ada_api_key:
        raise ValueError("Ada API key is required")

    # Construct Ada bot URL
    ada_bot_url = f"https://{bot_handle}.ada.support"

    return ada_api_key, ada_bot_url

def delete_ada_source(source_id, ada_api_key=None, ada_bot_url=None):
    # If credentials not provided, get them from user input
    if not ada_api_key or not ada_bot_url:
        ada_api_key, ada_bot_url = get_deletion_credentials()

    # Construct the API endpoint URL for deleting a specific knowledge source
    url = f"{ada_bot_url}/api/v2/knowledge/sources/{source_id}"

    # Send DELETE request to Ada API
    res = requests.delete(
        url,
        headers={
            "Authorization": f"Bearer {ada_api_key}",
            "Content-Type": "application/json"
        }
    )
    
    # Check if deletion was successful (204 = No Content, indicating successful deletion)
    if res.status_code == 204:
        print(f"Deleted Ada knowledge source: {source_id}")
    else:
        # Log error details if deletion failed
        print(f"Failed to delete knowledge source {source_id}.")
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")

if __name__ == "__main__":
    # Support both old and new usage patterns
    if len(sys.argv) == 2:
        # Old usage: python delete.py <SOURCE_ID>
        # Prompt user for credentials
        source_id = sys.argv[1]
        delete_ada_source(source_id)
    elif len(sys.argv) == 4:
        # New usage: python delete.py <SOURCE_ID> <ADA_BOT_URL> <ADA_API_KEY>
        # Use provided credentials
        source_id = sys.argv[1]
        ada_bot_url = sys.argv[2]
        ada_api_key = sys.argv[3]
        delete_ada_source(source_id, ada_api_key, ada_bot_url)
    else:
        print("Usage:")
        print("  python delete.py <SOURCE_ID>")
        print("  python delete.py <SOURCE_ID> <ADA_BOT_URL> <ADA_API_KEY>")
        sys.exit(1)