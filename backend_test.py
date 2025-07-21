#!/usr/bin/env python3
"""
FafoV2 Media Center Backend API Test Suite
Tests all API endpoints for the media center application
"""

import requests
import sys
import json
from datetime import datetime
from urllib.parse import quote

class FafoV2APITester:
    def __init__(self, base_url="https://092b3f52-c2e5-41c2-9c33-f4d4e4755f51.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_media_ids = []
        self.created_list_ids = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details and success:
            print(f"   Details: {details}")

    def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}"

            return True, response
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        success, response = self.make_request('GET', '')
        if success and response.status_code == 200:
            try:
                data = response.json()
                if 'message' in data and 'FafoV2' in data['message']:
                    self.log_test("Root Endpoint", True, f"Message: {data['message']}")
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected response: {data}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Root Endpoint", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Root Endpoint", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_stats_endpoint(self):
        """Test the stats endpoint"""
        success, response = self.make_request('GET', 'stats')
        if success and response.status_code == 200:
            try:
                data = response.json()
                required_keys = ['total_media_items', 'total_custom_lists', 'categories']
                if all(key in data for key in required_keys):
                    self.log_test("Stats Endpoint", True, f"Stats: {data}")
                    return True
                else:
                    self.log_test("Stats Endpoint", False, f"Missing required keys in response: {data}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Stats Endpoint", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Stats Endpoint", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_categories_endpoint(self):
        """Test the categories endpoint"""
        success, response = self.make_request('GET', 'categories')
        if success and response.status_code == 200:
            try:
                data = response.json()
                expected_categories = ['movies', 'tv_series', 'live_tv', 'youtube']
                if isinstance(data, dict) and all(cat in data for cat in expected_categories):
                    self.log_test("Categories Endpoint", True, f"Categories: {data}")
                    return True
                else:
                    self.log_test("Categories Endpoint", False, f"Missing expected categories: {data}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Categories Endpoint", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Categories Endpoint", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_create_media_item(self):
        """Test creating a media item"""
        media_data = {
            "title": "Test Movie",
            "url": "https://example.com/test-movie.mp4",
            "media_type": "direct_link",
            "category": "movies",
            "description": "A test movie for API testing"
        }
        
        success, response = self.make_request('POST', 'media', data=media_data)
        if success and response.status_code == 200:
            try:
                data = response.json()
                if 'id' in data and data['title'] == media_data['title']:
                    self.created_media_ids.append(data['id'])
                    self.log_test("Create Media Item", True, f"Created media with ID: {data['id']}")
                    return True, data['id']
                else:
                    self.log_test("Create Media Item", False, f"Invalid response structure: {data}")
                    return False, None
            except json.JSONDecodeError:
                self.log_test("Create Media Item", False, "Invalid JSON response")
                return False, None
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Create Media Item", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False, None

    def test_youtube_media_item(self):
        """Test creating a YouTube media item"""
        youtube_data = {
            "title": "Test YouTube Video",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - safe test video
            "media_type": "youtube",
            "category": "youtube",
            "description": "A test YouTube video"
        }
        
        success, response = self.make_request('POST', 'media', data=youtube_data)
        if success and response.status_code == 200:
            try:
                data = response.json()
                if 'id' in data:
                    self.created_media_ids.append(data['id'])
                    # Check if YouTube info was extracted
                    has_thumbnail = data.get('thumbnail') is not None
                    self.log_test("Create YouTube Media Item", True, 
                                f"Created YouTube media with ID: {data['id']}, Thumbnail extracted: {has_thumbnail}")
                    return True, data['id']
                else:
                    self.log_test("Create YouTube Media Item", False, f"Invalid response structure: {data}")
                    return False, None
            except json.JSONDecodeError:
                self.log_test("Create YouTube Media Item", False, "Invalid JSON response")
                return False, None
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Create YouTube Media Item", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False, None

    def test_get_media_items(self):
        """Test retrieving all media items"""
        success, response = self.make_request('GET', 'media')
        if success and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Media Items", True, f"Retrieved {len(data)} media items")
                    return True
                else:
                    self.log_test("Get All Media Items", False, f"Expected list, got: {type(data)}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Get All Media Items", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Get All Media Items", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_get_media_by_category(self):
        """Test retrieving media items by category"""
        success, response = self.make_request('GET', 'media', params={'category': 'movies'})
        if success and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    # Check if all items are movies
                    all_movies = all(item.get('category') == 'movies' for item in data)
                    self.log_test("Get Media by Category", all_movies, 
                                f"Retrieved {len(data)} movie items, All movies: {all_movies}")
                    return all_movies
                else:
                    self.log_test("Get Media by Category", False, f"Expected list, got: {type(data)}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Get Media by Category", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Get Media by Category", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_get_single_media_item(self, media_id):
        """Test retrieving a single media item"""
        if not media_id:
            self.log_test("Get Single Media Item", False, "No media ID provided")
            return False
            
        success, response = self.make_request('GET', f'media/{media_id}')
        if success and response.status_code == 200:
            try:
                data = response.json()
                if 'id' in data and data['id'] == media_id:
                    self.log_test("Get Single Media Item", True, f"Retrieved media item: {data['title']}")
                    return True
                else:
                    self.log_test("Get Single Media Item", False, f"ID mismatch or invalid structure: {data}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Get Single Media Item", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Get Single Media Item", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_video_info_endpoint(self):
        """Test video info extraction"""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        success, response = self.make_request('GET', 'video/info', params={'url': test_url})
        if success and response.status_code == 200:
            try:
                data = response.json()
                required_fields = ['title', 'url']
                if all(field in data for field in required_fields):
                    self.log_test("Video Info Endpoint", True, f"Extracted info for: {data['title']}")
                    return True
                else:
                    self.log_test("Video Info Endpoint", False, f"Missing required fields: {data}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Video Info Endpoint", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Video Info Endpoint", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_video_stream_endpoint(self):
        """Test video stream URL generation"""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        success, response = self.make_request('GET', 'video/stream', params={'url': test_url})
        if success and response.status_code == 200:
            try:
                data = response.json()
                required_fields = ['title', 'stream_url']
                if all(field in data for field in required_fields):
                    self.log_test("Video Stream Endpoint", True, f"Generated stream for: {data['title']}")
                    return True
                else:
                    self.log_test("Video Stream Endpoint", False, f"Missing required fields: {data}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Video Stream Endpoint", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Video Stream Endpoint", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_create_custom_list(self):
        """Test creating a custom list"""
        list_data = {
            "name": "Test Playlist",
            "description": "A test playlist for API testing"
        }
        
        success, response = self.make_request('POST', 'lists', data=list_data)
        if success and response.status_code == 200:
            try:
                data = response.json()
                if 'id' in data and data['name'] == list_data['name']:
                    self.created_list_ids.append(data['id'])
                    self.log_test("Create Custom List", True, f"Created list with ID: {data['id']}")
                    return True, data['id']
                else:
                    self.log_test("Create Custom List", False, f"Invalid response structure: {data}")
                    return False, None
            except json.JSONDecodeError:
                self.log_test("Create Custom List", False, "Invalid JSON response")
                return False, None
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Create Custom List", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False, None

    def test_get_custom_lists(self):
        """Test retrieving all custom lists"""
        success, response = self.make_request('GET', 'lists')
        if success and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Custom Lists", True, f"Retrieved {len(data)} custom lists")
                    return True
                else:
                    self.log_test("Get Custom Lists", False, f"Expected list, got: {type(data)}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Get Custom Lists", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Get Custom Lists", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_add_item_to_list(self, list_id, media_id):
        """Test adding a media item to a custom list"""
        if not list_id or not media_id:
            self.log_test("Add Item to List", False, "Missing list_id or media_id")
            return False
            
        success, response = self.make_request('POST', f'lists/{list_id}/items/{media_id}')
        if success and response.status_code == 200:
            try:
                data = response.json()
                if 'message' in data and 'successfully' in data['message']:
                    self.log_test("Add Item to List", True, f"Added item to list: {data['message']}")
                    return True
                else:
                    self.log_test("Add Item to List", False, f"Unexpected response: {data}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Add Item to List", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Add Item to List", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def test_get_list_items(self, list_id):
        """Test retrieving items from a custom list"""
        if not list_id:
            self.log_test("Get List Items", False, "No list ID provided")
            return False
            
        success, response = self.make_request('GET', f'lists/{list_id}/items')
        if success and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get List Items", True, f"Retrieved {len(data)} items from list")
                    return True
                else:
                    self.log_test("Get List Items", False, f"Expected list, got: {type(data)}")
                    return False
            except json.JSONDecodeError:
                self.log_test("Get List Items", False, "Invalid JSON response")
                return False
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Get List Items", False, f"Status: {response.status_code if success else 'N/A'}, Error: {error_msg}")
            return False

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete created media items
        for media_id in self.created_media_ids:
            success, response = self.make_request('DELETE', f'media/{media_id}')
            if success and response.status_code == 200:
                print(f"   ✅ Deleted media item: {media_id}")
            else:
                print(f"   ❌ Failed to delete media item: {media_id}")
        
        # Delete created lists
        for list_id in self.created_list_ids:
            success, response = self.make_request('DELETE', f'lists/{list_id}')
            if success and response.status_code == 200:
                print(f"   ✅ Deleted custom list: {list_id}")
            else:
                print(f"   ❌ Failed to delete custom list: {list_id}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting FafoV2 Media Center API Tests")
        print(f"🔗 Testing API at: {self.base_url}")
        print("=" * 60)

        # Basic endpoint tests
        self.test_root_endpoint()
        self.test_stats_endpoint()
        self.test_categories_endpoint()

        # Media item tests
        media_success, media_id = self.test_create_media_item()
        youtube_success, youtube_id = self.test_youtube_media_item()
        self.test_get_media_items()
        self.test_get_media_by_category()
        
        if media_id:
            self.test_get_single_media_item(media_id)

        # Video processing tests
        self.test_video_info_endpoint()
        self.test_video_stream_endpoint()

        # Custom list tests
        list_success, list_id = self.test_create_custom_list()
        self.test_get_custom_lists()
        
        if list_success and media_success and list_id and media_id:
            self.test_add_item_to_list(list_id, media_id)
            self.test_get_list_items(list_id)

        # Cleanup
        self.cleanup_test_data()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! API is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed.")
            return 1

def main():
    """Main test runner"""
    tester = FafoV2APITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())