import requests
from markdownify import markdownify as md
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='sync.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

PYLON_API_KEY = "YOUR_PYLON_API_KEY"
ADA_API_KEY = "471951f1295c907712d2dd06dc79a3a3"

def log_and_print(msg):
    print(msg)
    logging.info(msg)

def get_pylon_kb():
    res = requests.get(
        "https://api.usepylon.com/knowledge-bases",
        headers={"Authorization": f"Bearer {PYLON_API_KEY}","Content-Type": "application/json"}
    )
    res.raise_for_status()
    data = res.json()["data"]
    kb_id = data[0]["id"]
    kb_name = data[0]["title"]
    log_and_print(f"Found Pylon KB: {kb_name} (ID: {kb_id})")
    return kb_id, kb_name

def get_articles(kb_id):
    res = requests.get(
        f"https://api.usepylon.com/knowledge-bases/{kb_id}/articles?limit=50",
        headers={"Authorization": f"Bearer {PYLON_API_KEY}", "Content-Type": "application/json"}
    )
    res.raise_for_status()
    articles = res.json()["data"]
    log_and_print(f"Retrieved {len(articles)} articles.")
    return articles

def create_ada_source(kb_id, kb_name):
    payload = {
        "id": kb_id,  # must match what you used in Postman
        "name": f"Pylon ({kb_name or 'Untitled'})"
    }

    log_and_print(f"Creating Ada knowledge source with: {payload}")

    res = requests.post(
        "https://hasan-test-gr.ada.support/api/v2/knowledge/sources",
        headers={
            "Authorization": f"Bearer {ADA_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    try:
        res.raise_for_status()
    except Exception:
        print("Ada response:", res.text)
        raise

    source_id = payload["id"]
    log_and_print(f"Created Ada knowledge source: {source_id}")

    with open("source_ids.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {source_id}\n")

    return source_id

def upsert_articles(articles, source_id):
    formatted = []

    for article in articles:
        content = md(article.get("current_published_content_html", "") or "")
        updated_at = (
            article.get("updated_at")
            or article.get("modified_at")
            or datetime.utcnow().isoformat() + "Z"
        )

        formatted.append({
            "id": article.get("id") or article.get("_id"),
            "name": article.get("title") or article.get("name") or "Untitled",
            "content": content,
            "knowledge_source_id": source_id,
            "external_updated": updated_at
        })

    log_and_print(f"Uploading {len(formatted)} articles to Ada.")

    res = requests.post(
        "https://hasan-test-gr.ada.support/api/v2/knowledge/bulk/articles/",
        headers={
            "Authorization": f"Bearer {ADA_API_KEY}",
            "Content-Type": "application/json"
        },
        json=formatted
    )

    try:
        res.raise_for_status()
    except Exception:
        print("Ada response:", res.text)
        raise

    log_and_print(f"Uploaded {len(formatted)} articles to Ada.")

if __name__ == "__main__":
    try:
        kb_id, kb_name = get_pylon_kb()
        articles = get_articles(kb_id)
        ada_source_id = create_ada_source(kb_id, kb_name)
        upsert_articles(articles, ada_source_id)
        log_and_print("Sync completed successfully.")
        log_and_print(f"To delete this source, run: python delete.py {ada_source_id}")
    except Exception as e:
        logging.error(f"Sync failed: {e}")
        print(f"Error: {e}")
