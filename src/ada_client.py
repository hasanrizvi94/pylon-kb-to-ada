import requests
import logging
from typing import Dict, Any
from .config import config

logger = logging.getLogger(__name__)

class AdaClient:
    def __init__(self):
        self.api_key = config.get_ada_api_key()
        self.base_url = config.get_ada_base_url()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_knowledge_source(self, source_id: str, name: str) -> Dict[str, Any]:
        """Create a new knowledge source in Ada."""
        url = f"{self.base_url}/api/v2/knowledge/sources"
        payload = {
            "id": source_id,
            "name": name
        }
        
        try:
            logger.info(f"Creating Ada knowledge source: {payload}")
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Successfully created knowledge source: {source_id}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to create knowledge source {source_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def upload_article(self, source_id: str, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload an article to Ada knowledge source."""
        url = f"{self.base_url}/api/v2/knowledge/sources/{source_id}/articles"
        
        try:
            response = requests.post(url, json=article_data, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Successfully uploaded article: {article_data.get('title', 'Unknown')}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to upload article {article_data.get('title', 'Unknown')}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def delete_knowledge_source(self, source_id: str) -> bool:
        """Delete a knowledge source from Ada."""
        url = f"{self.base_url}/api/v2/knowledge/sources/{source_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 204:
                logger.info(f"Successfully deleted knowledge source: {source_id}")
                return True
            else:
                logger.error(f"Failed to delete knowledge source {source_id}. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except requests.RequestException as e:
            logger.error(f"Failed to delete knowledge source {source_id}: {e}")
            raise