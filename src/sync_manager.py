import logging
from datetime import datetime
from markdownify import markdownify as md
from typing import List, Dict, Any
from .pylon_client import PylonClient
from .ada_client import AdaClient
from .config import config

logger = logging.getLogger(__name__)

class SyncManager:
    def __init__(self):
        self.pylon_client = PylonClient()
        self.ada_client = AdaClient()
        self.source_ids_file = config.get_source_ids_file()
    
    def setup_logging(self):
        """Configure logging for the sync process."""
        log_file = config.get_log_file()
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
    
    def log_and_print(self, message: str):
        """Log message and print to console."""
        print(message)
        logger.info(message)
    
    def save_source_id(self, source_id: str, kb_name: str):
        """Save source ID with timestamp to file."""
        timestamp = datetime.now().isoformat()
        with open(self.source_ids_file, 'a') as f:
            f.write(f"{timestamp} - {source_id} - {kb_name}\n")
        self.log_and_print(f"Saved source ID {source_id} to {self.source_ids_file}")
    
    def convert_html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to Markdown."""
        if not html_content:
            return ""
        return md(html_content, heading_style="ATX")
    
    def prepare_article_data(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare article data for Ada upload."""
        content = self.convert_html_to_markdown(article.get("content", ""))
        
        return {
            "id": article["id"],
            "title": article["title"],
            "content": content,
            "created_at": article.get("created_at"),
            "updated_at": article.get("updated_at")
        }
    
    def sync_knowledge_base(self) -> str:
        """Sync knowledge base from Pylon to Ada."""
        try:
            # Get Pylon knowledge base
            kb_id, kb_name = self.pylon_client.get_first_knowledge_base()
            
            # Get articles from Pylon
            articles = self.pylon_client.get_articles(kb_id)
            
            if not articles:
                self.log_and_print("No articles found to sync")
                return None
            
            # Create Ada knowledge source
            source_name = f"Pylon ({kb_name or 'Untitled'})"
            self.ada_client.create_knowledge_source(kb_id, source_name)
            
            # Save source ID
            self.save_source_id(kb_id, kb_name)
            
            # Upload articles to Ada
            successful_uploads = 0
            for article in articles:
                try:
                    article_data = self.prepare_article_data(article)
                    self.ada_client.upload_article(kb_id, article_data)
                    successful_uploads += 1
                except Exception as e:
                    logger.error(f"Failed to upload article {article.get('title', 'Unknown')}: {e}")
                    continue
            
            self.log_and_print(f"Sync completed. {successful_uploads}/{len(articles)} articles uploaded successfully")
            return kb_id
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise
    
    def delete_knowledge_source(self, source_id: str) -> bool:
        """Delete a knowledge source from Ada."""
        try:
            return self.ada_client.delete_knowledge_source(source_id)
        except Exception as e:
            logger.error(f"Delete operation failed: {e}")
            raise