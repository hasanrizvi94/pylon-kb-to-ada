import requests
from markdownify import markdownify as md
import logging
from datetime import datetime
import hashlib
import time

# Configure logging
logging.basicConfig(
    filename='update_sync.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def log_and_print(msg, bot_handle=None, source_id=None):
    # Add bot handle and source ID context to message
    if bot_handle and source_id:
        formatted_msg = f"[{bot_handle}:{source_id}] {msg}"
    elif bot_handle:
        formatted_msg = f"[{bot_handle}] {msg}"
    else:
        formatted_msg = msg

    print(formatted_msg)
    logging.info(formatted_msg)

def get_content_hash(content):
    """Generate hash of article content for comparison."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def get_pylon_articles(kb_id, pylon_api_key, bot_handle=None, source_id=None):
    """Fetch all articles from Pylon knowledge base."""
    res = requests.get(
        f"https://api.usepylon.com/knowledge-bases/{kb_id}/articles?limit=200",
        headers={
            "Authorization": f"Bearer {pylon_api_key}",
            "Content-Type": "application/json"
        }
    )
    res.raise_for_status()
    articles = res.json()["data"]

    # Process articles into standardized format with content hash
    processed_articles = {}
    for article in articles:
        content = md(article.get("current_published_content_html", "") or "")
        if content.strip():  # Only include articles with content
            article_id = article.get("id") or article.get("_id")
            processed_articles[article_id] = {
                "id": article_id,
                "title": article.get("title") or article.get("name") or "Untitled",
                "content": content,
                "content_hash": get_content_hash(content),
                "updated_at": (
                    article.get("updated_at")
                    or article.get("modified_at")
                    or datetime.utcnow().isoformat() + "Z"
                )
            }

    log_and_print(f"Retrieved {len(processed_articles)} articles from Pylon", bot_handle, source_id)
    return processed_articles

def get_ada_articles(source_id, ada_api_key, ada_bot_url, bot_handle=None):
    """Fetch all articles from Ada knowledge source."""
    res = requests.get(
        f"{ada_bot_url}/api/v2/knowledge/articles/",
        headers={
            "Authorization": f"Bearer {ada_api_key}",
            "Content-Type": "application/json"
        },
        params={
            "knowledge_source_id": source_id,
            "limit": 100
        }
    )
    res.raise_for_status()
    articles = res.json().get("data", [])

    # Process articles into standardized format with content hash
    processed_articles = {}
    for article in articles:
        article_id = article.get("id")
        content = article.get("content", "")
        processed_articles[article_id] = {
            "id": article_id,
            "title": article.get("name", ""),
            "content": content,
            "content_hash": get_content_hash(content),
            "updated_at": article.get("external_updated", "")
        }

    log_and_print(f"Retrieved {len(processed_articles)} articles from Ada", bot_handle, source_id)
    return processed_articles

def bulk_upsert_articles(articles, source_id, ada_api_key, ada_bot_url, bot_handle=None):
    """Bulk create/update articles in Ada using the bulk upsert endpoint."""
    if not articles:
        return

    # Format articles for bulk upsert (as array, not object)
    formatted_articles = []
    for article in articles:
        formatted_articles.append({
            "id": article["id"],
            "name": article["title"],
            "content": article["content"],
            "knowledge_source_id": source_id,
            "external_updated": article["updated_at"]
        })

    res = requests.post(
        f"{ada_bot_url}/api/v2/knowledge/bulk/articles/",
        headers={
            "Authorization": f"Bearer {ada_api_key}",
            "Content-Type": "application/json"
        },
        json=formatted_articles
    )

    try:
        res.raise_for_status()
        article_titles = [article["title"] for article in articles]
        log_and_print(f"Bulk upserted {len(articles)} articles: {', '.join(article_titles[:3])}{'...' if len(articles) > 3 else ''}", bot_handle, source_id)
    except Exception:
        print("Ada response:", res.text)
        raise

def delete_articles_from_ada(article_ids, ada_api_key, ada_bot_url, bot_handle=None, source_id=None):
    """Delete articles from Ada using the correct endpoint."""
    if not article_ids:
        return

    res = requests.delete(
        f"{ada_bot_url}/api/v2/knowledge/articles/",
        headers={
            "Authorization": f"Bearer {ada_api_key}",
            "Content-Type": "application/json"
        },
        params={
            "id": article_ids
        }
    )

    try:
        res.raise_for_status()
        log_and_print(f"Deleted {len(article_ids)} articles: {', '.join(article_ids[:3])}{'...' if len(article_ids) > 3 else ''}", bot_handle, source_id)
    except Exception:
        print("Ada response:", res.text)
        raise

def perform_delta_sync(kb_id, source_id, pylon_api_key, ada_api_key, ada_bot_url, bot_handle):
    """Perform delta comparison and sync between Pylon and Ada."""
    log_and_print("Starting delta sync...", bot_handle, source_id)

    # Fetch articles from both systems
    pylon_articles = get_pylon_articles(kb_id, pylon_api_key, bot_handle, source_id)
    ada_articles = get_ada_articles(source_id, ada_api_key, ada_bot_url, bot_handle)

    pylon_ids = set(pylon_articles.keys())
    ada_ids = set(ada_articles.keys())

    # Articles in Pylon not in Ada → CREATE
    to_create = pylon_ids - ada_ids
    log_and_print(f"Articles to create: {len(to_create)}", bot_handle, source_id)

    # Articles in both but content differs → UPDATE
    to_update = []
    for article_id in pylon_ids & ada_ids:
        pylon_hash = pylon_articles[article_id]["content_hash"]
        ada_hash = ada_articles[article_id]["content_hash"]
        if pylon_hash != ada_hash:
            to_update.append(article_id)
            log_and_print(f"Content changed for '{pylon_articles[article_id]['title']}' (ID: {article_id})", bot_handle, source_id)
            log_and_print(f"  Pylon hash: {pylon_hash}", bot_handle, source_id)
            log_and_print(f"  Ada hash: {ada_hash}", bot_handle, source_id)

    log_and_print(f"Articles to update: {len(to_update)}", bot_handle, source_id)

    # Bulk upsert for both creates and updates
    articles_to_upsert = []
    for article_id in to_create:
        articles_to_upsert.append(pylon_articles[article_id])
    for article_id in to_update:
        articles_to_upsert.append(pylon_articles[article_id])

    if articles_to_upsert:
        bulk_upsert_articles(articles_to_upsert, source_id, ada_api_key, ada_bot_url, bot_handle)

    # Articles in Ada not in Pylon → DELETE
    to_delete = list(ada_ids - pylon_ids)
    log_and_print(f"Articles to delete: {len(to_delete)}", bot_handle, source_id)

    if to_delete:
        delete_articles_from_ada(to_delete, ada_api_key, ada_bot_url, bot_handle, source_id)

    log_and_print(f"Delta sync completed: {len(to_create)} created, {len(to_update)} updated, {len(to_delete)} deleted", bot_handle, source_id)

# def continuous_sync(kb_id, source_id, pylon_api_key, ada_api_key, ada_bot_url, interval_seconds=300):
#     """Run continuous sync at regular intervals."""
#     log_and_print(f"Starting continuous sync (interval: {interval_seconds} seconds)")

#     while True:
#         try:
#             perform_delta_sync(kb_id, source_id, pylon_api_key, ada_api_key, ada_bot_url)
#             log_and_print(f"Sync completed. Next sync in {interval_seconds} seconds...")
#             time.sleep(interval_seconds)
#         except KeyboardInterrupt:
#             log_and_print("Continuous sync stopped by user")
#             break
#         except Exception as e:
#             logging.error(f"Sync failed: {e}")
#             log_and_print(f"Error during sync: {e}. Retrying in {interval_seconds} seconds...")
#             time.sleep(interval_seconds)

def get_user_credentials():
    """Prompt user for their API credentials and bot handle."""
    print("Welcome to the Pylon-to-Ada Update Sync Tool!")
    print("Please provide the following information:\n")

    bot_handle = input("Enter your Ada bot handle (e.g., 'my-bot' for my-bot.ada.support): ").strip()
    if not bot_handle:
        raise ValueError("Bot handle is required")

    ada_api_key = input("Enter your Ada API key: ").strip()
    if not ada_api_key:
        raise ValueError("Ada API key is required")

    pylon_api_key = input("Enter your Pylon API key: ").strip()
    if not pylon_api_key:
        raise ValueError("Pylon API key is required")

    ada_bot_url = f"https://{bot_handle}.ada.support"

    print(f"\nConfiguration:")
    print(f"Ada Bot URL: {ada_bot_url}")
    print(f"Ada API Key: {ada_api_key[:10]}...")
    print(f"Pylon API Key: {pylon_api_key[:10]}...\n")

    return pylon_api_key, ada_api_key, ada_bot_url

if __name__ == "__main__":
    try:
        # Get credentials
        pylon_api_key, ada_api_key, ada_bot_url = get_user_credentials()

        # Get knowledge base and source IDs
        kb_id = input("Enter your Pylon knowledge base ID: ").strip()
        if not kb_id:
            raise ValueError("Knowledge base ID is required")

        source_id = input("Enter your Ada knowledge source ID: ").strip()
        if not source_id:
            raise ValueError("Ada source ID is required")

        # Extract bot handle from URL
        bot_handle = ada_bot_url.replace("https://", "").replace(".ada.support", "")

        # Run single delta sync
        perform_delta_sync(kb_id, source_id, pylon_api_key, ada_api_key, ada_bot_url, bot_handle)

        # # Get sync interval
        # interval_input = input("Enter sync interval in seconds (default: 300): ").strip()
        # interval = int(interval_input) if interval_input else 300

        # # Choose sync mode
        # mode = input("Run once (1) or continuous (2)? Enter 1 or 2: ").strip()

        # if mode == "1":
        #     perform_delta_sync(kb_id, source_id, pylon_api_key, ada_api_key, ada_bot_url)
        # else:
        #     continuous_sync(kb_id, source_id, pylon_api_key, ada_api_key, ada_bot_url, interval)

    except Exception as e:
        logging.error(f"Update sync failed: {e}")
        print(f"Error: {e}")