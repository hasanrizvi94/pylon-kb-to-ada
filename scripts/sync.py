#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.sync_manager import SyncManager

def main():
    sync_manager = SyncManager()
    sync_manager.setup_logging()
    
    try:
        source_id = sync_manager.sync_knowledge_base()
        if source_id:
            print(f"To delete this source, run: python scripts/delete.py {source_id}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
