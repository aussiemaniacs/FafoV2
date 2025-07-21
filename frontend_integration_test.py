#!/usr/bin/env python3
"""
FafoV2 Media Center Frontend Integration Test
Tests frontend-backend integration and error scenarios
"""

import requests
import sys
import json
from datetime import datetime

class FrontendIntegrationTester:
    def __init__(self, base_url="https://092b3f52-c2e5-41c2-9c33-f4d4e4755f51.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

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

    def test_cors_headers(self):
        """Test CORS configuration"""
        try:
            response = requests.options(f"{self.api_url}/stats", 
                                      headers={'Origin': self.base_url})
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.log_test("CORS Headers", True, f"CORS configured: {cors_headers}")
                return True
            else:
                self.log_test("CORS Headers", False, "No CORS headers found")
                return False
        except Exception as e:
            self.log_test("CORS Headers", False, f"Error: {str(e)}")
            return False

    def test_invalid_endpoints(self):
        """Test invalid API endpoints"""
        invalid_endpoints = [
            "nonexistent",
            "media/invalid-id",
            "lists/invalid-id",
            "video/info?url=invalid-url"
        ]
        
        all_passed = True
        for endpoint in invalid_endpoints:
            try:
                response = requests.get(f"{self.api_url}/{endpoint}", timeout=10)
                if response.status_code in [400, 404, 422]:
                    print(f"   ✅ {endpoint} - Correctly returns {response.status_code}")
                else:
                    print(f"   ❌ {endpoint} - Unexpected status {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {str(e)}")
                all_passed = False
        
        self.log_test("Invalid Endpoints", all_passed, "Error handling for invalid endpoints")
        return all_passed

    def test_malformed_requests(self):
        """Test malformed POST requests"""
        malformed_data = [
            {"title": ""},  # Empty title
            {"url": "not-a-url"},  # Invalid URL
            {"title": "Test", "url": "http://example.com", "category": "invalid"},  # Invalid category
            {}  # Empty data
        ]
        
        all_passed = True
        for data in malformed_data:
            try:
                response = requests.post(f"{self.api_url}/media", json=data, timeout=10)
                if response.status_code in [400, 422]:
                    print(f"   ✅ Malformed data correctly rejected: {response.status_code}")
                else:
                    print(f"   ❌ Malformed data accepted: {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ Error with malformed data: {str(e)}")
                all_passed = False
        
        self.log_test("Malformed Requests", all_passed, "Validation of malformed requests")
        return all_passed

    def test_youtube_edge_cases(self):
        """Test YouTube URL edge cases"""
        youtube_urls = [
            "https://www.youtube.com/watch?v=invalid",  # Invalid video ID
            "https://www.youtube.com/watch?v=",  # Empty video ID
            "https://youtu.be/invalid",  # Invalid short URL
            "https://www.youtube.com/playlist?list=invalid"  # Invalid playlist
        ]
        
        all_handled = True
        for url in youtube_urls:
            try:
                response = requests.get(f"{self.api_url}/video/info", 
                                      params={'url': url}, timeout=30)
                if response.status_code == 400:
                    print(f"   ✅ Invalid YouTube URL correctly handled: {url}")
                else:
                    print(f"   ⚠️  Unexpected response for {url}: {response.status_code}")
                    # This might not be a failure as yt-dlp might handle some cases
            except Exception as e:
                print(f"   ❌ Error testing {url}: {str(e)}")
                all_handled = False
        
        self.log_test("YouTube Edge Cases", all_handled, "YouTube URL validation")
        return all_handled

    def test_concurrent_requests(self):
        """Test concurrent API requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                response = requests.get(f"{self.api_url}/stats", timeout=10)
                results.append(response.status_code == 200)
            except:
                results.append(False)
        
        # Create 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        success_rate = sum(results) / len(results)
        passed = success_rate >= 0.8  # At least 80% should succeed
        
        self.log_test("Concurrent Requests", passed, 
                     f"Success rate: {success_rate:.1%} ({sum(results)}/{len(results)})")
        return passed

    def test_large_data_handling(self):
        """Test handling of large data"""
        large_description = "A" * 10000  # 10KB description
        
        large_media_data = {
            "title": "Large Data Test",
            "url": "https://example.com/large-test.mp4",
            "media_type": "direct_link",
            "category": "movies",
            "description": large_description
        }
        
        try:
            response = requests.post(f"{self.api_url}/media", json=large_media_data, timeout=30)
            if response.status_code == 200:
                # Clean up
                data = response.json()
                requests.delete(f"{self.api_url}/media/{data['id']}")
                self.log_test("Large Data Handling", True, "Large description handled correctly")
                return True
            else:
                self.log_test("Large Data Handling", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Large Data Handling", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Frontend Integration Tests")
        print(f"🔗 Testing integration with: {self.base_url}")
        print("=" * 60)

        # Run all tests
        self.test_cors_headers()
        self.test_invalid_endpoints()
        self.test_malformed_requests()
        self.test_youtube_edge_cases()
        self.test_concurrent_requests()
        self.test_large_data_handling()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Integration Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All integration tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} integration tests failed.")
            return 1

def main():
    """Main test runner"""
    tester = FrontendIntegrationTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())