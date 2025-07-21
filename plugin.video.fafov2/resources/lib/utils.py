#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FafoV2 Utility Functions
Common utilities for the addon
"""

import os
import json
import time
import uuid
import logging
import requests
from datetime import datetime
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(__name__)

class Utils:
    """Utility functions for FafoV2 addon"""
    
    def __init__(self):
        self.addon_data_path = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure the addon data directory exists"""
        if not xbmcvfs.exists(self.addon_data_path):
            xbmcvfs.mkdirs(self.addon_data_path)
    
    def get_current_timestamp(self):
        """Get current timestamp as string"""
        return datetime.now().isoformat()
    
    def generate_id(self):
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    def load_json_file(self, filename):
        """Load JSON data from file"""
        filepath = os.path.join(self.addon_data_path, filename)
        try:
            if xbmcvfs.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading JSON file {filename}: {e}")
            return {}
    
    def save_json_file(self, filename, data):
        """Save data to JSON file"""
        filepath = os.path.join(self.addon_data_path, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON file {filename}: {e}")
            return False
    
    def is_valid_url(self, url):
        """Check if URL is valid"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def make_request(self, url, timeout=10):
        """Make HTTP request with error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def format_duration(self, seconds):
        """Format duration in seconds to human readable format"""
        if not seconds:
            return "Unknown"
        
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes}:{secs:02d}"
        except:
            return "Unknown"
    
    def clean_filename(self, filename):
        """Clean filename for safe file operations"""
        import re
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip()
        return filename[:100]  # Limit length
    
    def log_info(self, message):
        """Log info message"""
        logger.info(message)
        if ADDON.getSettingBool('debug_logging'):
            xbmc.log(f"[FafoV2] {message}", xbmc.LOGINFO)
    
    def log_error(self, message, exception=None):
        """Log error message"""
        logger.error(message)
        xbmc.log(f"[FafoV2 ERROR] {message}", xbmc.LOGERROR)
        if exception:
            xbmc.log(f"[FafoV2 ERROR] Exception: {str(exception)}", xbmc.LOGERROR)
    
    def show_notification(self, title, message, notification_type='info', duration=5000):
        """Show Kodi notification"""
        icon_map = {
            'info': xbmcgui.NOTIFICATION_INFO,
            'warning': xbmcgui.NOTIFICATION_WARNING,
            'error': xbmcgui.NOTIFICATION_ERROR
        }
        
        icon = icon_map.get(notification_type, xbmcgui.NOTIFICATION_INFO)
        xbmcgui.Dialog().notification(title, message, icon, duration)
    
    def get_setting(self, setting_id, default=None):
        """Get addon setting value"""
        try:
            setting_type = type(default) if default is not None else str
            
            if setting_type == bool:
                return ADDON.getSettingBool(setting_id)
            elif setting_type == int:
                return ADDON.getSettingInt(setting_id)
            elif setting_type == float:
                return ADDON.getSettingNumber(setting_id)
            else:
                return ADDON.getSetting(setting_id) or default
        except:
            return default
    
    def set_setting(self, setting_id, value):
        """Set addon setting value"""
        try:
            if isinstance(value, bool):
                ADDON.setSettingBool(setting_id, value)
            elif isinstance(value, int):
                ADDON.setSettingInt(setting_id, value)
            elif isinstance(value, float):
                ADDON.setSettingNumber(setting_id, value)
            else:
                ADDON.setSetting(setting_id, str(value))
            return True
        except:
            return False