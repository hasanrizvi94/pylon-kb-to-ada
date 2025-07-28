import requests
import logging
from typing import List, Dict, Tuple, Any
from .config import config

logger = logging.getLogger(__name__)

class PylonClient:
    def __init__(self):
        self.api_key = config.get_pylon_api_key()
        self.base_url = config.get_pylon_base_url()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_knowledge_bases(self) -> List[Dict[str, Any]]:
        """Fetch all knowledge bases from Pylon."""
        url = f"{self.base_url}/knowledge-bases"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()["data"]
            logger.info(f"Retrieved {len(data)} knowledge bases from Pylon")
            return data
        except requests.RequestException as e:
            logger.error(f"Failed to fetch knowledge bases: {e}")
            raise
    
    def get_first_knowledge_base(self) -> Tuple[str, str]:
        """Get the first knowledge base ID and name."""
        knowledge_bases = self.get_knowledge_bases()
        if not knowledge_bases:
            raise ValueError("No knowledge bases found")
        
        kb = knowledge_bases[0]
        kb_id = kb["id"]
        kb_name = kb["title"]
        logger.info(f"Using knowledge base: {kb_name} (ID: {kb_id})")
        return kb_id, kb_name
    
    def get_articles(self, kb_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Fetch articles from a specific knowledge base."""
        if limit is None:
            limit = config.get_article_limit()
        
        url = f"{self.base_url}/knowledge-bases/{kb_id}/articles"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            articles = response.json()["data"]
            logger.info(f"Retrieved {len(articles)} articles from knowledge base {kb_id}")
            return articles
        except requests.RequestException as e:
            logger.error(f"Failed to fetch articles for KB {kb_id}: {e}")
            raise