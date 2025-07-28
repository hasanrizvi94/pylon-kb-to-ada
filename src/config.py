import os
import yaml
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

class Config:
    def __init__(self, config_file: Optional[str] = None):
        self.config_data = {}
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
    
    def get_pylon_api_key(self) -> str:
        return os.getenv('PYLON_API_KEY') or self.config_data.get('pylon', {}).get('api_key', '')
    
    def get_ada_api_key(self) -> str:
        return os.getenv('ADA_API_KEY') or self.config_data.get('ada', {}).get('api_key', '')
    
    def get_ada_base_url(self) -> str:
        return os.getenv('ADA_BASE_URL') or self.config_data.get('ada', {}).get('base_url', 'https://hasan-test-gr.ada.support')
    
    def get_pylon_base_url(self) -> str:
        return os.getenv('PYLON_BASE_URL') or self.config_data.get('pylon', {}).get('base_url', 'https://api.usepylon.com')
    
    def get_article_limit(self) -> int:
        return int(os.getenv('ARTICLE_LIMIT', '50')) or self.config_data.get('sync', {}).get('article_limit', 50)
    
    def get_log_file(self) -> str:
        return os.getenv('LOG_FILE') or self.config_data.get('logging', {}).get('file', 'sync.log')
    
    def get_source_ids_file(self) -> str:
        return os.getenv('SOURCE_IDS_FILE') or self.config_data.get('sync', {}).get('source_ids_file', 'source_ids.txt')

# Global config instance
config = Config('config.yaml')