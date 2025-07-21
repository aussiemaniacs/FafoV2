#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FafoV2 YouTube Handler
Handles YouTube video processing, search, and URL resolution using yt-dlp
"""

import os
import re
import logging
import subprocess
import json
from urllib.parse import parse_qs, urlparse
import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(__name__)

class YouTubeHandler:
    """Handle YouTube operations with yt-dlp integration"""
    
    def __init__(self):
        self.yt_dlp_available = self.check_yt_dlp_available()
        
    def check_yt_dlp_available(self):
        """Check if yt-dlp is available"""
        try:
            # Try to import yt-dlp
            import yt_dlp
            return True
        except ImportError:
            try:
                # Try system yt-dlp
                result = subprocess.run(['yt-dlp', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except:
                logger.warning("yt-dlp not available - YouTube functionality will be limited")
                return False
    
    def extract_video_id(self, url):
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, url):
        """Get video information using yt-dlp"""
        if not self.yt_dlp_available:
            # Fallback to basic info extraction
            video_id = self.extract_video_id(url)
            if video_id:
                return {
                    'title': f'YouTube Video {video_id}',
                    'url': url,
                    'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                    'description': 'YouTube video (yt-dlp not available for detailed info)'
                }
            return None
        
        try:
            if hasattr(self, '_yt_dlp_module'):
                # Use imported yt-dlp
                import yt_dlp
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'skip_download': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                return {
                    'title': info.get('title', 'Unknown'),
                    'url': url,
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', ''),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count')
                }
            else:
                # Use system yt-dlp
                cmd = [
                    'yt-dlp',
                    '--quiet',
                    '--no-warnings',
                    '--dump-json',
                    '--skip-download',
                    url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    return {
                        'title': info.get('title', 'Unknown'),
                        'url': url,
                        'thumbnail': info.get('thumbnail'),
                        'description': info.get('description', ''),
                        'duration': info.get('duration'),
                        'uploader': info.get('uploader'),
                        'view_count': info.get('view_count')
                    }
                    
        except Exception as e:
            logger.error(f"Error getting video info for {url}: {e}")
        
        return None
    
    def resolve_youtube_url(self, url, quality='720p'):
        """Resolve YouTube URL to playable stream"""
        if not self.yt_dlp_available:
            # Try to use Kodi's YouTube plugin if available
            try:
                if xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
                    video_id = self.extract_video_id(url)
                    if video_id:
                        return f'plugin://plugin.video.youtube/play/?video_id={video_id}'
            except:
                pass
            
            # Return original URL as fallback
            return url
        
        try:
            if hasattr(self, '_yt_dlp_module'):
                # Use imported yt-dlp
                import yt_dlp
                
                # Quality format selection
                format_selector = f'best[height<={quality[:-1]}]' if quality.endswith('p') else 'best'
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': format_selector
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    return info.get('url')
            else:
                # Use system yt-dlp
                format_selector = f'best[height<={quality[:-1]}]' if quality.endswith('p') else 'best'
                
                cmd = [
                    'yt-dlp',
                    '--quiet',
                    '--no-warnings',
                    '--format', format_selector,
                    '--get-url',
                    url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return result.stdout.strip()
                    
        except Exception as e:
            logger.error(f"Error resolving YouTube URL {url}: {e}")
        
        # Fallback to original URL
        return url
    
    def search_videos(self, query, max_results=20):
        """Search for YouTube videos"""
        if not self.yt_dlp_available:
            xbmcgui.Dialog().notification(
                "FafoV2",
                "YouTube search requires yt-dlp",
                xbmcgui.NOTIFICATION_WARNING,
                5000
            )
            return []
        
        try:
            search_url = f"ytsearch{max_results}:{query}"
            
            if hasattr(self, '_yt_dlp_module'):
                # Use imported yt-dlp
                import yt_dlp
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(search_url, download=False)
                    
                results = []
                for entry in info.get('entries', []):
                    if entry:
                        results.append({
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('webpage_url', ''),
                            'thumbnail': entry.get('thumbnail'),
                            'duration': entry.get('duration'),
                            'uploader': entry.get('uploader')
                        })
                        
                return results
            else:
                # Use system yt-dlp
                cmd = [
                    'yt-dlp',
                    '--quiet',
                    '--no-warnings',
                    '--dump-json',
                    '--skip-download',
                    '--flat-playlist',
                    search_url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    results = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            try:
                                entry = json.loads(line)
                                results.append({
                                    'title': entry.get('title', 'Unknown'),
                                    'url': entry.get('webpage_url', ''),
                                    'thumbnail': entry.get('thumbnail'),
                                    'duration': entry.get('duration'),
                                    'uploader': entry.get('uploader')
                                })
                            except:
                                continue
                    return results
                    
        except Exception as e:
            logger.error(f"Error searching YouTube for '{query}': {e}")
        
        return []
    
    def get_playlist_info(self, url):
        """Get playlist information"""
        if not self.yt_dlp_available:
            return None
            
        try:
            if hasattr(self, '_yt_dlp_module'):
                # Use imported yt-dlp
                import yt_dlp
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                if 'entries' in info:
                    entries = []
                    for entry in info['entries'][:50]:  # Limit to 50 entries
                        if entry:
                            entries.append({
                                'title': entry.get('title', 'Unknown'),
                                'url': entry.get('webpage_url', ''),
                                'thumbnail': entry.get('thumbnail'),
                                'duration': entry.get('duration')
                            })
                    
                    return {
                        'title': info.get('title', 'Unknown Playlist'),
                        'entries': entries,
                        'entry_count': len(entries)
                    }
            else:
                # Use system yt-dlp
                cmd = [
                    'yt-dlp',
                    '--quiet',
                    '--no-warnings',
                    '--dump-json',
                    '--flat-playlist',
                    url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    entries = []
                    playlist_title = "Unknown Playlist"
                    
                    for line in result.stdout.strip().split('\n')[:50]:  # Limit to 50
                        if line:
                            try:
                                entry = json.loads(line)
                                if entry.get('_type') == 'playlist':
                                    playlist_title = entry.get('title', playlist_title)
                                else:
                                    entries.append({
                                        'title': entry.get('title', 'Unknown'),
                                        'url': entry.get('webpage_url', ''),
                                        'thumbnail': entry.get('thumbnail'),
                                        'duration': entry.get('duration')
                                    })
                            except:
                                continue
                    
                    return {
                        'title': playlist_title,
                        'entries': entries,
                        'entry_count': len(entries)
                    }
                    
        except Exception as e:
            logger.error(f"Error getting playlist info for {url}: {e}")
            
        return None