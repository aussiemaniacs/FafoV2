#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FafoV2 Lists Manager
Handles custom lists and category management for the addon
"""

import os
import json
import logging
from datetime import datetime
import xbmc
import xbmcaddon
import xbmcgui

from .utils import Utils

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(__name__)

class ListsManager:
    """Manage custom lists and media categories"""
    
    def __init__(self):
        self.utils = Utils()
        self.lists_file = 'custom_lists.json'
        self.categories_file = 'categories.json'
    
    def get_all_lists(self):
        """Get all custom lists"""
        lists_data = self.utils.load_json_file(self.lists_file)
        return lists_data.get('lists', [])
    
    def get_list(self, list_id):
        """Get a specific list by ID"""
        lists = self.get_all_lists()
        for list_data in lists:
            if list_data.get('id') == list_id:
                return list_data
        return None
    
    def create_list(self, name, description=''):
        """Create a new custom list"""
        try:
            lists_data = self.utils.load_json_file(self.lists_file)
            if 'lists' not in lists_data:
                lists_data['lists'] = []
            
            new_list = {
                'id': self.utils.generate_id(),
                'name': name,
                'description': description,
                'items': [],
                'created_date': self.utils.get_current_timestamp(),
                'updated_date': self.utils.get_current_timestamp()
            }
            
            lists_data['lists'].append(new_list)
            
            if self.utils.save_json_file(self.lists_file, lists_data):
                logger.info(f"Created custom list: {name}")
                return True
            
        except Exception as e:
            logger.error(f"Error creating list '{name}': {e}")
        
        return False
    
    def delete_list(self, list_id):
        """Delete a custom list"""
        try:
            lists_data = self.utils.load_json_file(self.lists_file)
            lists = lists_data.get('lists', [])
            
            # Find and remove the list
            updated_lists = [l for l in lists if l.get('id') != list_id]
            
            if len(updated_lists) < len(lists):
                lists_data['lists'] = updated_lists
                if self.utils.save_json_file(self.lists_file, lists_data):
                    logger.info(f"Deleted custom list: {list_id}")
                    return True
            
        except Exception as e:
            logger.error(f"Error deleting list {list_id}: {e}")
        
        return False
    
    def rename_list(self, list_id, new_name):
        """Rename a custom list"""
        try:
            lists_data = self.utils.load_json_file(self.lists_file)
            lists = lists_data.get('lists', [])
            
            for list_data in lists:
                if list_data.get('id') == list_id:
                    list_data['name'] = new_name
                    list_data['updated_date'] = self.utils.get_current_timestamp()
                    break
            
            if self.utils.save_json_file(self.lists_file, lists_data):
                logger.info(f"Renamed list {list_id} to: {new_name}")
                return True
            
        except Exception as e:
            logger.error(f"Error renaming list {list_id}: {e}")
        
        return False
    
    def add_item_to_list(self, list_id, item):
        """Add an item to a custom list"""
        try:
            lists_data = self.utils.load_json_file(self.lists_file)
            lists = lists_data.get('lists', [])
            
            for list_data in lists:
                if list_data.get('id') == list_id:
                    # Check if item already exists (by URL)
                    existing_urls = [i.get('url') for i in list_data.get('items', [])]
                    if item.get('url') not in existing_urls:
                        list_data.setdefault('items', []).append(item)
                        list_data['updated_date'] = self.utils.get_current_timestamp()
                        
                        if self.utils.save_json_file(self.lists_file, lists_data):
                            logger.info(f"Added item to list {list_id}: {item.get('title')}")
                            return True
                    else:
                        logger.info(f"Item already exists in list {list_id}: {item.get('title')}")
                        return True  # Not an error, just already exists
                    break
            
        except Exception as e:
            logger.error(f"Error adding item to list {list_id}: {e}")
        
        return False
    
    def remove_item_from_list(self, list_id, item_url):
        """Remove an item from a custom list"""
        try:
            lists_data = self.utils.load_json_file(self.lists_file)
            lists = lists_data.get('lists', [])
            
            for list_data in lists:
                if list_data.get('id') == list_id:
                    items = list_data.get('items', [])
                    updated_items = [i for i in items if i.get('url') != item_url]
                    
                    if len(updated_items) < len(items):
                        list_data['items'] = updated_items
                        list_data['updated_date'] = self.utils.get_current_timestamp()
                        
                        if self.utils.save_json_file(self.lists_file, lists_data):
                            logger.info(f"Removed item from list {list_id}")
                            return True
                    break
            
        except Exception as e:
            logger.error(f"Error removing item from list {list_id}: {e}")
        
        return False
    
    def get_category_items(self, category):
        """Get all items in a specific category"""
        categories_data = self.utils.load_json_file(self.categories_file)
        return categories_data.get(category, [])
    
    def add_item_to_category(self, category, item):
        """Add an item to a category"""
        try:
            categories_data = self.utils.load_json_file(self.categories_file)
            
            if category not in categories_data:
                categories_data[category] = []
            
            # Check if item already exists (by URL)
            existing_urls = [i.get('url') for i in categories_data[category]]
            if item.get('url') not in existing_urls:
                # Add unique ID if not present
                if 'id' not in item:
                    item['id'] = self.utils.generate_id()
                
                categories_data[category].append(item)
                
                if self.utils.save_json_file(self.categories_file, categories_data):
                    logger.info(f"Added item to category {category}: {item.get('title')}")
                    return True
            else:
                logger.info(f"Item already exists in category {category}: {item.get('title')}")
                return True  # Not an error, just already exists
            
        except Exception as e:
            logger.error(f"Error adding item to category {category}: {e}")
        
        return False
    
    def remove_item_from_category(self, category, item_url):
        """Remove an item from a category"""
        try:
            categories_data = self.utils.load_json_file(self.categories_file)
            
            if category in categories_data:
                items = categories_data[category]
                updated_items = [i for i in items if i.get('url') != item_url]
                
                if len(updated_items) < len(items):
                    categories_data[category] = updated_items
                    
                    if self.utils.save_json_file(self.categories_file, categories_data):
                        logger.info(f"Removed item from category {category}")
                        return True
            
        except Exception as e:
            logger.error(f"Error removing item from category {category}: {e}")
        
        return False
    
    def get_category_stats(self):
        """Get statistics for all categories"""
        categories_data = self.utils.load_json_file(self.categories_file)
        stats = {}
        
        for category in ['movies', 'tv_series', 'live_tv', 'youtube']:
            stats[category] = len(categories_data.get(category, []))
        
        return stats
    
    def get_lists_stats(self):
        """Get statistics for custom lists"""
        lists = self.get_all_lists()
        return {
            'total_lists': len(lists),
            'total_items': sum(len(l.get('items', [])) for l in lists)
        }
    
    def search_items(self, query, search_in=['movies', 'tv_series', 'live_tv', 'youtube']):
        """Search for items across categories"""
        results = []
        categories_data = self.utils.load_json_file(self.categories_file)
        
        query_lower = query.lower()
        
        for category in search_in:
            items = categories_data.get(category, [])
            for item in items:
                title = item.get('title', '').lower()
                description = item.get('description', '').lower()
                
                if query_lower in title or query_lower in description:
                    item_copy = item.copy()
                    item_copy['category'] = category
                    results.append(item_copy)
        
        return results
    
    def export_lists(self):
        """Export all lists and categories to a single file"""
        try:
            export_data = {
                'lists': self.get_all_lists(),
                'categories': self.utils.load_json_file(self.categories_file),
                'export_date': self.utils.get_current_timestamp(),
                'addon_version': ADDON.getAddonInfo('version')
            }
            
            if self.utils.save_json_file('fafov2_export.json', export_data):
                return os.path.join(self.utils.addon_data_path, 'fafov2_export.json')
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
        
        return None
    
    def import_lists(self, filepath):
        """Import lists and categories from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            
            # Import lists
            if 'lists' in import_data:
                for list_data in import_data['lists']:
                    # Generate new ID to avoid conflicts
                    list_data['id'] = self.utils.generate_id()
                    list_data['name'] = f"{list_data['name']} (Imported)"
                    
                    if self.create_list(list_data['name'], list_data.get('description', '')):
                        # Add items to the new list
                        lists = self.get_all_lists()
                        new_list = lists[-1]  # Get the just created list
                        
                        for item in list_data.get('items', []):
                            self.add_item_to_list(new_list['id'], item)
                        
                        imported_count += 1
            
            # Import categories
            if 'categories' in import_data:
                categories_data = self.utils.load_json_file(self.categories_file)
                
                for category, items in import_data['categories'].items():
                    for item in items:
                        if category not in categories_data:
                            categories_data[category] = []
                        
                        # Check if item already exists
                        existing_urls = [i.get('url') for i in categories_data[category]]
                        if item.get('url') not in existing_urls:
                            categories_data[category].append(item)
                            imported_count += 1
                
                self.utils.save_json_file(self.categories_file, categories_data)
            
            logger.info(f"Imported {imported_count} items")
            return imported_count
            
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return 0