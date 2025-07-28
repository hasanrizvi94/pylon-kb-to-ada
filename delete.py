import requests
import sys

ADA_API_KEY = "471951f1295c907712d2dd06dc79a3a3"

def delete_ada_source(source_id):
    url = f"https://hasan-test-gr.ada.support/api/v2/knowledge/sources/{source_id}"
    res = requests.delete(
        url,
        headers={
            "Authorization": f"Bearer {ADA_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    if res.status_code == 204:
        print(f"Deleted Ada knowledge source: {source_id}")
    else:
        print(f"Failed to delete knowledge source {source_id}.")
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete.py <SOURCE_ID>")
        sys.exit(1)

    source_id = sys.argv[1]
    delete_ada_source(source_id)