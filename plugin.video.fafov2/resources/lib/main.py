#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FafoV2 Main Addon Logic
Handles all addon functionality including menus, video playback, and list management
"""

import sys
import os
import json
import logging
from urllib.parse import urlencode, quote_plus, unquote_plus
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from .utils import Utils
from .youtube_handler import YouTubeHandler
from .lists_manager import ListsManager

# Get addon instance
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_DATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))

# Ensure data directory exists
if not xbmcvfs.exists(ADDON_DATA_PATH):
    xbmcvfs.mkdirs(ADDON_DATA_PATH)

logger = logging.getLogger(__name__)

class FafoV2Addon:
    """Main addon class handling all functionality"""
    
    def __init__(self, plugin_handle, base_url):
        self.plugin_handle = plugin_handle
        self.base_url = base_url
        self.utils = Utils()
        self.youtube_handler = YouTubeHandler()
        self.lists_manager = ListsManager()
        
        # Set content type for video addon
        xbmcplugin.setContent(self.plugin_handle, 'videos')
        
        logger.info("FafoV2Addon initialized")

    def build_url(self, action, **kwargs):
        """Build plugin URL with action and parameters"""
        params = {'action': action}
        params.update(kwargs)
        return f"{self.base_url}?{urlencode(params)}"

    def add_directory_item(self, title, action, icon=None, fanart=None, **kwargs):
        """Add a directory item to the current listing"""
        url = self.build_url(action, **kwargs)
        list_item = xbmcgui.ListItem(label=title)
        
        # Set artwork
        if icon:
            list_item.setArt({'icon': icon, 'thumb': icon})
        if fanart:
            list_item.setArt({'fanart': fanart})
            
        # Add context menu for lists
        if action != 'custom_lists' and action != 'settings':
            context_menu = [
                ('Add to Custom List', f'RunPlugin({self.build_url("add_to_list", url=kwargs.get("url", ""), title=title)})')
            ]
            list_item.addContextMenuItems(context_menu)
        
        xbmcplugin.addDirectoryItem(
            self.plugin_handle,
            url,
            list_item,
            isFolder=True
        )

    def add_video_item(self, title, url, thumbnail=None, description=None, duration=None):
        """Add a video item that can be played"""
        play_url = self.build_url('play_video', url=url, title=title)
        list_item = xbmcgui.ListItem(label=title)
        
        # Set video info
        info_labels = {
            'title': title,
            'plot': description or title,
            'mediatype': 'video'
        }
        
        if duration:
            info_labels['duration'] = duration
            
        list_item.setInfo('video', info_labels)
        
        # Set artwork
        if thumbnail:
            list_item.setArt({
                'icon': thumbnail,
                'thumb': thumbnail,
                'poster': thumbnail,
                'fanart': thumbnail
            })
        
        # Set as playable
        list_item.setProperty('IsPlayable', 'true')
        
        # Add context menu
        context_menu = [
            ('Add to Custom List', f'RunPlugin({self.build_url("add_to_list", url=url, title=title)})')
        ]
        list_item.addContextMenuItems(context_menu)
        
        xbmcplugin.addDirectoryItem(
            self.plugin_handle,
            play_url,
            list_item,
            isFolder=False
        )

    def show_main_menu(self):
        """Show the main addon menu"""
        logger.info("Showing main menu")
        
        # Main categories
        self.add_directory_item(
            "🎬 Movies",
            "movies",
            icon=os.path.join(ADDON.getAddonInfo('path'), 'resources', 'media', 'movies.png')
        )
        
        self.add_directory_item(
            "📺 TV Series",
            "tv_series",
            icon=os.path.join(ADDON.getAddonInfo('path'), 'resources', 'media', 'tv.png')
        )
        
        self.add_directory_item(
            "📡 Live TV",
            "live_tv",
            icon=os.path.join(ADDON.getAddonInfo('path'), 'resources', 'media', 'live.png')
        )
        
        self.add_directory_item(
            "▶️ YouTube",
            "youtube",
            icon=os.path.join(ADDON.getAddonInfo('path'), 'resources', 'media', 'youtube.png')
        )
        
        self.add_directory_item(
            "📝 Custom Lists",
            "custom_lists",
            icon=os.path.join(ADDON.getAddonInfo('path'), 'resources', 'media', 'lists.png')
        )
        
        # Separator
        self.add_directory_item("─────────────────", "separator")
        
        # Tools
        self.add_directory_item("🔍 YouTube Search", "youtube_search")
        self.add_directory_item("🔗 Add Direct Link", "add_direct_link")
        self.add_directory_item("⚙️ Settings", "settings")
        
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def show_movies(self):
        """Show movies category"""
        logger.info("Showing movies")
        
        movies = self.lists_manager.get_category_items('movies')
        
        if not movies:
            # Show sample/placeholder items
            self.add_video_item(
                "Sample Movie Trailer",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                description="Sample movie trailer - Add your own movies using 'Add Direct Link'"
            )
        else:
            for movie in movies:
                self.add_video_item(
                    movie['title'],
                    movie['url'],
                    movie.get('thumbnail'),
                    movie.get('description'),
                    movie.get('duration')
                )
        
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def show_tv_series(self):
        """Show TV series category"""
        logger.info("Showing TV series")
        
        series = self.lists_manager.get_category_items('tv_series')
        
        if not series:
            self.add_video_item(
                "Sample TV Series Trailer",
                "https://www.youtube.com/watch?v=jNQXAC9IVRw",
                description="Sample TV series trailer - Add your own shows using 'Add Direct Link'"
            )
        else:
            for show in series:
                self.add_video_item(
                    show['title'],
                    show['url'],
                    show.get('thumbnail'),
                    show.get('description'),
                    show.get('duration')
                )
        
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def show_live_tv(self):
        """Show live TV category"""
        logger.info("Showing live TV")
        
        live_streams = self.lists_manager.get_category_items('live_tv')
        
        if not live_streams:
            self.add_video_item(
                "Sample Live Stream",
                "https://www.youtube.com/watch?v=9Auq9mYxFEE",  # Sample 24/7 stream
                description="Sample live stream - Add your own live TV streams using 'Add Direct Link'"
            )
        else:
            for stream in live_streams:
                self.add_video_item(
                    stream['title'],
                    stream['url'],
                    stream.get('thumbnail'),
                    stream.get('description')
                )
        
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def show_youtube(self):
        """Show YouTube category and options"""
        logger.info("Showing YouTube")
        
        # YouTube options
        self.add_directory_item("🔍 Search YouTube", "youtube_search")
        
        # Separator
        self.add_directory_item("─────────────────", "separator")
        
        # Show saved YouTube videos
        youtube_items = self.lists_manager.get_category_items('youtube')
        
        if not youtube_items:
            self.add_video_item(
                "Rick Astley - Never Gonna Give You Up",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                description="Sample YouTube video - Use search to add more videos"
            )
        else:
            for item in youtube_items:
                self.add_video_item(
                    item['title'],
                    item['url'],
                    item.get('thumbnail'),
                    item.get('description'),
                    item.get('duration')
                )
        
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def show_custom_lists(self):
        """Show custom lists menu"""
        logger.info("Showing custom lists")
        
        # List management options
        self.add_directory_item("➕ Create New List", "create_list")
        self.add_directory_item("🗂️ Manage Lists", "manage_lists")
        
        # Separator
        self.add_directory_item("─────────────────", "separator")
        
        # Show existing lists
        lists = self.lists_manager.get_all_lists()
        
        if lists:
            for list_data in lists:
                item_count = len(list_data.get('items', []))
                title = f"{list_data['name']} ({item_count} items)"
                self.add_directory_item(
                    title,
                    "view_list",
                    list_id=list_data['id']
                )
        else:
            self.add_directory_item("No custom lists created yet", "separator")
        
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def youtube_search(self):
        """Handle YouTube search"""
        logger.info("YouTube search requested")
        
        # Get search query from user
        keyboard = xbmc.Keyboard('', 'Enter search term')
        keyboard.doModal()
        
        if keyboard.isConfirmed():
            query = keyboard.getText()
            if query:
                try:
                    # Show progress dialog
                    progress = xbmcgui.DialogProgress()
                    progress.create("FafoV2", "Searching YouTube...")
                    
                    results = self.youtube_handler.search_videos(query)
                    progress.close()
                    
                    if results:
                        for video in results:
                            self.add_video_item(
                                video['title'],
                                video['url'],
                                video.get('thumbnail'),
                                video.get('description'),
                                video.get('duration')
                            )
                        xbmcplugin.endOfDirectory(self.plugin_handle)
                    else:
                        xbmcgui.Dialog().notification(
                            "FafoV2",
                            "No results found",
                            xbmcgui.NOTIFICATION_INFO,
                            3000
                        )
                except Exception as e:
                    logger.error(f"YouTube search error: {e}")
                    progress.close()
                    xbmcgui.Dialog().notification(
                        "FafoV2",
                        f"Search failed: {str(e)}",
                        xbmcgui.NOTIFICATION_ERROR,
                        5000
                    )

    def add_direct_link(self):
        """Add a direct link to media"""
        logger.info("Add direct link requested")
        
        # Get URL from user
        keyboard = xbmc.Keyboard('http://', 'Enter media URL')
        keyboard.doModal()
        
        if keyboard.isConfirmed():
            url = keyboard.getText()
            if url:
                # Get title
                keyboard = xbmc.Keyboard('', 'Enter title')
                keyboard.doModal()
                
                if keyboard.isConfirmed():
                    title = keyboard.getText() or "Unknown Media"
                    
                    # Get category
                    categories = ['movies', 'tv_series', 'live_tv', 'youtube']
                    dialog = xbmcgui.Dialog()
                    category_index = dialog.select('Select Category', categories)
                    
                    if category_index >= 0:
                        category = categories[category_index]
                        
                        # Add to category
                        media_item = {
                            'title': title,
                            'url': url,
                            'category': category,
                            'added_date': self.utils.get_current_timestamp()
                        }
                        
                        # Try to get video info if it's a YouTube URL
                        if 'youtube.com' in url or 'youtu.be' in url:
                            try:
                                video_info = self.youtube_handler.get_video_info(url)
                                media_item.update({
                                    'thumbnail': video_info.get('thumbnail'),
                                    'description': video_info.get('description'),
                                    'duration': video_info.get('duration')
                                })
                            except Exception as e:
                                logger.warning(f"Could not get YouTube info: {e}")
                        
                        if self.lists_manager.add_item_to_category(category, media_item):
                            xbmcgui.Dialog().notification(
                                "FafoV2",
                                f"Added to {category}",
                                xbmcgui.NOTIFICATION_INFO,
                                3000
                            )
                        else:
                            xbmcgui.Dialog().notification(
                                "FafoV2",
                                "Failed to add item",
                                xbmcgui.NOTIFICATION_ERROR,
                                3000
                            )

    def play_video(self, url, title):
        """Play a video URL"""
        logger.info(f"Playing video: {title} - {url}")
        
        try:
            # Show progress dialog
            progress = xbmcgui.DialogProgress()
            progress.create("FafoV2", "Resolving video URL...")
            
            # Resolve URL using YouTube handler if it's a YouTube URL
            if 'youtube.com' in url or 'youtu.be' in url:
                resolved_url = self.youtube_handler.resolve_youtube_url(url)
            else:
                resolved_url = url
            
            progress.close()
            
            if resolved_url:
                # Create list item for playback
                list_item = xbmcgui.ListItem(label=title)
                list_item.setInfo('video', {'title': title, 'mediatype': 'video'})
                list_item.setProperty('IsPlayable', 'true')
                
                # Start playback
                xbmc.Player().play(resolved_url, list_item)
            else:
                xbmcgui.Dialog().notification(
                    "FafoV2",
                    "Could not resolve video URL",
                    xbmcgui.NOTIFICATION_ERROR,
                    5000
                )
                
        except Exception as e:
            logger.error(f"Error playing video: {e}")
            progress.close()
            xbmcgui.Dialog().notification(
                "FafoV2",
                f"Playback failed: {str(e)}",
                xbmcgui.NOTIFICATION_ERROR,
                5000
            )

    def create_custom_list(self):
        """Create a new custom list"""
        logger.info("Create custom list requested")
        
        # Get list name
        keyboard = xbmc.Keyboard('', 'Enter list name')
        keyboard.doModal()
        
        if keyboard.isConfirmed():
            name = keyboard.getText()
            if name:
                # Get description (optional)
                keyboard = xbmc.Keyboard('', 'Enter description (optional)')
                keyboard.doModal()
                description = keyboard.getText() if keyboard.isConfirmed() else ''
                
                if self.lists_manager.create_list(name, description):
                    xbmcgui.Dialog().notification(
                        "FafoV2",
                        f"List '{name}' created",
                        xbmcgui.NOTIFICATION_INFO,
                        3000
                    )
                    # Refresh the current directory
                    xbmc.executebuiltin('Container.Refresh')
                else:
                    xbmcgui.Dialog().notification(
                        "FafoV2",
                        "Failed to create list",
                        xbmcgui.NOTIFICATION_ERROR,
                        3000
                    )

    def view_custom_list(self, list_id):
        """View contents of a custom list"""
        logger.info(f"Viewing custom list: {list_id}")
        
        list_data = self.lists_manager.get_list(list_id)
        if list_data:
            items = list_data.get('items', [])
            
            if items:
                for item in items:
                    self.add_video_item(
                        item['title'],
                        item['url'],
                        item.get('thumbnail'),
                        item.get('description'),
                        item.get('duration')
                    )
            else:
                self.add_directory_item("List is empty", "separator")
                
            xbmcplugin.endOfDirectory(self.plugin_handle)
        else:
            xbmcgui.Dialog().notification(
                "FafoV2",
                "List not found",
                xbmcgui.NOTIFICATION_ERROR,
                3000
            )

    def add_to_custom_list(self, list_id, url, title):
        """Add item to a custom list"""
        if not list_id:
            # Let user select a list
            lists = self.lists_manager.get_all_lists()
            if lists:
                list_names = [l['name'] for l in lists]
                dialog = xbmcgui.Dialog()
                selected = dialog.select('Select List', list_names)
                if selected >= 0:
                    list_id = lists[selected]['id']
            else:
                xbmcgui.Dialog().notification(
                    "FafoV2",
                    "No lists available. Create one first.",
                    xbmcgui.NOTIFICATION_WARNING,
                    3000
                )
                return
        
        if list_id:
            item = {
                'title': title,
                'url': url,
                'added_date': self.utils.get_current_timestamp()
            }
            
            if self.lists_manager.add_item_to_list(list_id, item):
                xbmcgui.Dialog().notification(
                    "FafoV2",
                    f"Added '{title}' to list",
                    xbmcgui.NOTIFICATION_INFO,
                    3000
                )
            else:
                xbmcgui.Dialog().notification(
                    "FafoV2",
                    "Failed to add to list",
                    xbmcgui.NOTIFICATION_ERROR,
                    3000
                )

    def manage_custom_lists(self):
        """Manage existing custom lists"""
        logger.info("Manage custom lists requested")
        
        lists = self.lists_manager.get_all_lists()
        if not lists:
            xbmcgui.Dialog().notification(
                "FafoV2",
                "No lists to manage",
                xbmcgui.NOTIFICATION_INFO,
                3000
            )
            return
        
        list_names = [f"{l['name']} ({len(l.get('items', []))} items)" for l in lists]
        dialog = xbmcgui.Dialog()
        selected = dialog.select('Select List to Manage', list_names)
        
        if selected >= 0:
            list_data = lists[selected]
            
            # Management options
            options = ['View Items', 'Rename List', 'Delete List']
            action = dialog.select(f'Manage: {list_data["name"]}', options)
            
            if action == 0:  # View Items
                self.view_custom_list(list_data['id'])
            elif action == 1:  # Rename List
                keyboard = xbmc.Keyboard(list_data['name'], 'Enter new name')
                keyboard.doModal()
                if keyboard.isConfirmed():
                    new_name = keyboard.getText()
                    if new_name and self.lists_manager.rename_list(list_data['id'], new_name):
                        xbmcgui.Dialog().notification(
                            "FafoV2",
                            "List renamed",
                            xbmcgui.NOTIFICATION_INFO,
                            3000
                        )
            elif action == 2:  # Delete List
                if dialog.yesno("FafoV2", f"Delete list '{list_data['name']}'?"):
                    if self.lists_manager.delete_list(list_data['id']):
                        xbmcgui.Dialog().notification(
                            "FafoV2",
                            "List deleted",
                            xbmcgui.NOTIFICATION_INFO,
                            3000
                        )

    def delete_custom_list(self, list_id):
        """Delete a custom list"""
        if self.lists_manager.delete_list(list_id):
            xbmcgui.Dialog().notification(
                "FafoV2",
                "List deleted",
                xbmcgui.NOTIFICATION_INFO,
                3000
            )
            xbmc.executebuiltin('Container.Refresh')
        else:
            xbmcgui.Dialog().notification(
                "FafoV2",
                "Failed to delete list",
                xbmcgui.NOTIFICATION_ERROR,
                3000
            )

    def open_settings(self):
        """Open addon settings"""
        ADDON.openSettings()