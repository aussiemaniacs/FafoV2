#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FafoV2 Kodi Addon - Main Entry Point
Advanced Media Center with YouTube, Live TV, and Custom Lists
Author: aussiemaniacs
Version: 2.0.0
"""

import sys
import logging
from urllib.parse import parse_qsl
import xbmcaddon
import xbmcgui
import xbmcplugin

# Get addon info
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_VERSION = ADDON.getAddonInfo('version')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=f'[{ADDON_ID}] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the addon"""
    try:
        # Log addon startup
        logger.info(f"Starting {ADDON_NAME} v{ADDON_VERSION}")
        
        # Get plugin handle and parameters
        plugin_handle = int(sys.argv[1])
        base_url = sys.argv[0]
        params = dict(parse_qsl(sys.argv[2][1:]))
        
        logger.info(f"Plugin called with params: {params}")
        
        # Import and initialize main addon logic
        from resources.lib.main import FafoV2Addon
        
        # Create addon instance
        addon = FafoV2Addon(plugin_handle, base_url)
        
        # Route to appropriate handler based on action
        action = params.get('action')
        
        if action is None:
            # Show main menu
            addon.show_main_menu()
        elif action == 'movies':
            addon.show_movies()
        elif action == 'tv_series':
            addon.show_tv_series()
        elif action == 'live_tv':
            addon.show_live_tv()
        elif action == 'youtube':
            addon.show_youtube()
        elif action == 'custom_lists':
            addon.show_custom_lists()
        elif action == 'add_to_list':
            list_id = params.get('list_id')
            url = params.get('url')
            title = params.get('title')
            addon.add_to_custom_list(list_id, url, title)
        elif action == 'play_video':
            url = params.get('url')
            title = params.get('title', 'Unknown')
            addon.play_video(url, title)
        elif action == 'youtube_search':
            addon.youtube_search()
        elif action == 'add_direct_link':
            addon.add_direct_link()
        elif action == 'manage_lists':
            addon.manage_custom_lists()
        elif action == 'create_list':
            addon.create_custom_list()
        elif action == 'delete_list':
            list_id = params.get('list_id')
            addon.delete_custom_list(list_id)
        elif action == 'view_list':
            list_id = params.get('list_id')
            addon.view_custom_list(list_id)
        elif action == 'settings':
            addon.open_settings()
        else:
            logger.warning(f"Unknown action: {action}")
            addon.show_main_menu()
            
    except Exception as e:
        logger.error(f"Error in main(): {e}", exc_info=True)
        xbmcgui.Dialog().notification(
            ADDON_NAME,
            f"Error: {str(e)}",
            xbmcgui.NOTIFICATION_ERROR,
            5000
        )

if __name__ == '__main__':
    main()