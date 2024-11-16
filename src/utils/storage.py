import json
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ClosetStorage:
    def __init__(self):
        self.storage_dir = Path('data/closet')
        self.closet_file = self.storage_dir / 'closet.json'
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure storage directory and file exist"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        if not self.closet_file.exists():
            self.closet_file.write_text('{"items": []}')
    
    def _load_closet(self):
        """Load the current closet data"""
        try:
            with open(self.closet_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Corrupted closet file, creating new one")
            default_closet = {"items": []}
            self._save_closet(default_closet)
            return default_closet
            
    def _save_closet(self, closet_data):
        """Save the closet data"""
        with open(self.closet_file, 'w') as f:
            json.dump(closet_data, f, indent=2)
    
    def add_item(self, item_data, image_filename):
        """Add a new clothing item to the closet"""
        try:
            closet = self._load_closet()
            
            # Add metadata to the item
            item_data['id'] = str(len(closet['items']) + 1)  # Simple ID generation
            item_data['date_added'] = datetime.now().isoformat()
            item_data['image_filename'] = image_filename
            
            # Add to closet
            closet['items'].append(item_data)
            
            # Save updated closet
            self._save_closet(closet)
            
            logger.info(f"Added item {item_data['id']} to closet")
            return item_data['id']
            
        except Exception as e:
            logger.error(f"Error adding item to closet: {e}")
            raise
    
    def get_all_items(self):
        """Get all items in the closet"""
        try:
            closet = self._load_closet()
            return closet['items']
        except Exception as e:
            logger.error(f"Error getting closet items: {e}")
            raise
    
    def get_item(self, item_id):
        """Get a specific item from the closet"""
        try:
            closet = self._load_closet()
            for item in closet['items']:
                if item['id'] == item_id:
                    return item
            return None
        except Exception as e:
            logger.error(f"Error getting item {item_id}: {e}")
            raise