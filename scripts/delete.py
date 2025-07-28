#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.sync_manager import SyncManager

def main():
    if len(sys.argv) != 2:
        print("Usage: python delete.py <SOURCE_ID>")
        sys.exit(1)
    
    source_id = sys.argv[1]
    sync_manager = SyncManager()
    sync_manager.setup_logging()
    
    try:
        success = sync_manager.delete_knowledge_source(source_id)
        if success:
            print(f"Successfully deleted Ada knowledge source: {source_id}")
        else:
            print(f"Failed to delete knowledge source: {source_id}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()