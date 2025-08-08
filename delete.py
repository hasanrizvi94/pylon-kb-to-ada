import requests
import sys

# Ada API authentication key
ADA_API_KEY = "YOUR_ADA_API_KEY"

def delete_ada_source(source_id):
    # Construct the API endpoint URL for deleting a specific knowledge source
    url = f"https://hasan-gen-test.ada.support/api/v2/knowledge/sources/{source_id}"
    
    # Send DELETE request to Ada API
    res = requests.delete(
        url,
        headers={
            "Authorization": f"Bearer {ADA_API_KEY}",
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
    # Validate command line arguments
    if len(sys.argv) != 2:
        print("Usage: python delete.py <SOURCE_ID>")
        sys.exit(1)

    # Extract source ID from command line argument
    source_id = sys.argv[1]
    delete_ada_source(source_id)