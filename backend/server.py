from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import yt_dlp
import validators
import asyncio
import json
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class MediaItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    url: str
    media_type: str  # youtube, direct_link, live_tv, playlist
    category: str  # movies, tv_series, live_tv, youtube
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    quality: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MediaItemCreate(BaseModel):
    title: str
    url: str
    media_type: str
    category: str
    thumbnail: Optional[str] = None
    description: Optional[str] = None

class CustomList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    items: List[str] = []  # List of MediaItem IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CustomListCreate(BaseModel):
    name: str
    description: Optional[str] = None

class VideoInfo(BaseModel):
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    quality: Optional[str] = None
    formats: List[Dict[str, Any]] = []

class PlaylistInfo(BaseModel):
    title: str
    url: str
    entries: List[VideoInfo]
    thumbnail: Optional[str] = None

# Configure yt-dlp
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'format': 'best[height<=720]'
}

def extract_video_info(url: str) -> Dict[str, Any]:
    """Extract video information using yt-dlp"""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        logging.error(f"Error extracting video info: {e}")
        raise HTTPException(status_code=400, detail=f"Unable to extract video info: {str(e)}")

def is_playlist(url: str) -> bool:
    """Check if URL is a playlist"""
    playlist_indicators = ['playlist', 'list=', '/c/', '/channel/', '/user/']
    return any(indicator in url.lower() for indicator in playlist_indicators)

def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    return validators.url(url) or url.startswith('http')


# API Routes

@api_router.get("/")
async def root():
    return {"message": "FafoV2 Media Center API"}

# Media Items Routes
@api_router.post("/media", response_model=MediaItem)
async def create_media_item(input: MediaItemCreate):
    """Create a new media item"""
    if not validate_url(input.url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Extract additional info if it's a YouTube URL
    additional_info = {}
    if 'youtube.com' in input.url or 'youtu.be' in input.url:
        try:
            video_info = extract_video_info(input.url)
            additional_info = {
                'thumbnail': video_info.get('thumbnail'),
                'description': video_info.get('description', '')[:500],  # Limit description
                'duration': video_info.get('duration')
            }
        except Exception as e:
            logging.warning(f"Could not extract YouTube info: {e}")
    
    media_dict = input.dict()
    media_dict.update(additional_info)
    media_obj = MediaItem(**media_dict)
    
    await db.media_items.insert_one(media_obj.dict())
    return media_obj

@api_router.get("/media", response_model=List[MediaItem])
async def get_media_items(category: Optional[str] = None, media_type: Optional[str] = None):
    """Get all media items with optional filtering"""
    filter_dict = {}
    if category:
        filter_dict['category'] = category
    if media_type:
        filter_dict['media_type'] = media_type
    
    media_items = await db.media_items.find(filter_dict).to_list(1000)
    return [MediaItem(**item) for item in media_items]

@api_router.get("/media/{media_id}", response_model=MediaItem)
async def get_media_item(media_id: str):
    """Get a specific media item"""
    media_item = await db.media_items.find_one({"id": media_id})
    if not media_item:
        raise HTTPException(status_code=404, detail="Media item not found")
    return MediaItem(**media_item)

@api_router.delete("/media/{media_id}")
async def delete_media_item(media_id: str):
    """Delete a media item"""
    result = await db.media_items.delete_one({"id": media_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Media item not found")
    return {"message": "Media item deleted successfully"}

# Video Processing Routes
@api_router.get("/video/info")
async def get_video_info(url: str):
    """Get video information from URL"""
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    try:
        info = extract_video_info(url)
        
        # Format the response
        video_info = VideoInfo(
            title=info.get('title', 'Unknown'),
            url=url,
            thumbnail=info.get('thumbnail'),
            duration=info.get('duration'),
            quality=f"{info.get('height', 'Unknown')}p" if info.get('height') else None,
            formats=[{
                'format_id': fmt.get('format_id'),
                'ext': fmt.get('ext'),
                'quality': fmt.get('height'),
                'url': fmt.get('url')
            } for fmt in info.get('formats', [])[:5]]  # Limit to 5 formats
        )
        
        return video_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to process video: {str(e)}")

@api_router.get("/video/stream")
async def get_video_stream(url: str, quality: Optional[str] = "720"):
    """Get direct video stream URL"""
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    try:
        ydl_opts_stream = {
            'quiet': True,
            'no_warnings': True,
            'format': f'best[height<={quality}]'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts_stream) as ydl:
            info = ydl.extract_info(url, download=False)
            
        return {
            'title': info.get('title'),
            'stream_url': info.get('url'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to get stream: {str(e)}")

@api_router.get("/playlist/info")
async def get_playlist_info(url: str):
    """Get playlist information"""
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        if 'entries' not in info:
            raise HTTPException(status_code=400, detail="URL is not a playlist")
        
        # Process playlist entries
        entries = []
        for entry in info['entries'][:20]:  # Limit to 20 entries
            if entry:
                entries.append(VideoInfo(
                    title=entry.get('title', 'Unknown'),
                    url=entry.get('webpage_url', entry.get('url', '')),
                    thumbnail=entry.get('thumbnail'),
                    duration=entry.get('duration')
                ))
        
        playlist_info = PlaylistInfo(
            title=info.get('title', 'Unknown Playlist'),
            url=url,
            entries=entries,
            thumbnail=info.get('thumbnail')
        )
        
        return playlist_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to process playlist: {str(e)}")

# Custom Lists Routes
@api_router.post("/lists", response_model=CustomList)
async def create_custom_list(input: CustomListCreate):
    """Create a new custom list"""
    list_dict = input.dict()
    list_obj = CustomList(**list_dict)
    
    await db.custom_lists.insert_one(list_obj.dict())
    return list_obj

@api_router.get("/lists", response_model=List[CustomList])
async def get_custom_lists():
    """Get all custom lists"""
    lists = await db.custom_lists.find().to_list(1000)
    return [CustomList(**list_item) for list_item in lists]

@api_router.get("/lists/{list_id}", response_model=CustomList)
async def get_custom_list(list_id: str):
    """Get a specific custom list"""
    list_item = await db.custom_lists.find_one({"id": list_id})
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    return CustomList(**list_item)

@api_router.post("/lists/{list_id}/items/{media_id}")
async def add_item_to_list(list_id: str, media_id: str):
    """Add a media item to a custom list"""
    # Check if list exists
    list_item = await db.custom_lists.find_one({"id": list_id})
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    
    # Check if media item exists
    media_item = await db.media_items.find_one({"id": media_id})
    if not media_item:
        raise HTTPException(status_code=404, detail="Media item not found")
    
    # Add item to list if not already present
    if media_id not in list_item['items']:
        await db.custom_lists.update_one(
            {"id": list_id},
            {
                "$push": {"items": media_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    
    return {"message": "Item added to list successfully"}

@api_router.delete("/lists/{list_id}/items/{media_id}")
async def remove_item_from_list(list_id: str, media_id: str):
    """Remove a media item from a custom list"""
    result = await db.custom_lists.update_one(
        {"id": list_id},
        {
            "$pull": {"items": media_id},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="List not found or item not in list")
    
    return {"message": "Item removed from list successfully"}

@api_router.delete("/lists/{list_id}")
async def delete_custom_list(list_id: str):
    """Delete a custom list"""
    result = await db.custom_lists.delete_one({"id": list_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted successfully"}

@api_router.get("/lists/{list_id}/items", response_model=List[MediaItem])
async def get_list_items(list_id: str):
    """Get all media items in a custom list"""
    list_item = await db.custom_lists.find_one({"id": list_id})
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    
    # Get all media items in the list
    media_items = await db.media_items.find({"id": {"$in": list_item['items']}}).to_list(1000)
    return [MediaItem(**item) for item in media_items]

# Categories and Stats
@api_router.get("/categories")
async def get_categories():
    """Get all available categories with counts"""
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    
    result = await db.media_items.aggregate(pipeline).to_list(1000)
    categories = {item['_id']: item['count'] for item in result}
    
    # Ensure all main categories are present
    default_categories = ["movies", "tv_series", "live_tv", "youtube"]
    for cat in default_categories:
        if cat not in categories:
            categories[cat] = 0
    
    return categories

@api_router.get("/stats")
async def get_stats():
    """Get general statistics"""
    total_media = await db.media_items.count_documents({})
    total_lists = await db.custom_lists.count_documents({})
    
    return {
        "total_media_items": total_media,
        "total_custom_lists": total_lists,
        "categories": await get_categories()
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()