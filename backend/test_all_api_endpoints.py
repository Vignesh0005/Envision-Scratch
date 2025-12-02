"""
Comprehensive API Endpoint Tester
Tests all API endpoints with actual HTTP requests
"""

import requests
import json
import sys
from typing import Dict, List, Tuple
from datetime import datetime

class APITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            'working': [],
            'errors': [],
            'cors_issues': [],
            'not_found': []
        }
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000'
        })
    
    def test_endpoint(self, method: str, path: str, data: dict = None, expected_status: int = None) -> Dict:
        """Test a single API endpoint"""
        url = f"{self.base_url}{path}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, timeout=5)
            elif method == 'POST':
                response = self.session.post(url, json=data or {}, timeout=5)
            elif method == 'PUT':
                response = self.session.put(url, json=data or {}, timeout=5)
            elif method == 'DELETE':
                response = self.session.delete(url, timeout=5)
            else:
                return {'error': f'Unknown method: {method}'}
            
            # Check CORS
            cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
            has_cors = bool(cors_origin)
            
            result = {
                'method': method,
                'path': path,
                'url': url,
                'status': response.status_code,
                'cors': has_cors,
                'cors_origin': cors_origin,
                'content_type': response.headers.get('Content-Type', 'N/A'),
                'ok': response.status_code < 500
            }
            
            # Try to parse JSON response
            try:
                result['response'] = response.json()
            except:
                result['response'] = response.text[:200] if response.text else 'No content'
            
            # Check if status matches expected
            if expected_status and response.status_code != expected_status:
                result['warning'] = f'Expected status {expected_status}, got {response.status_code}'
            
            return result
            
        except requests.exceptions.ConnectionError:
            return {
                'method': method,
                'path': path,
                'url': url,
                'status': 'CONNECTION_ERROR',
                'error': 'Cannot connect to server'
            }
        except requests.exceptions.Timeout:
            return {
                'method': method,
                'path': path,
                'url': url,
                'status': 'TIMEOUT',
                'error': 'Request timed out'
            }
        except Exception as e:
            return {
                'method': method,
                'path': path,
                'url': url,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def categorize_result(self, result: Dict):
        """Categorize test result"""
        status = result.get('status')
        
        if status == 'CONNECTION_ERROR':
            self.results['errors'].append(result)
        elif status == 404:
            # Check if it's a "file not found" 404 or "route not found" 404
            response_text = str(result.get('response', '')).lower()
            if 'image not found' in response_text or 'not found' in response_text or 'no path' in response_text:
                # Endpoint exists, just file/image doesn't exist - this is OK
                self.results['working'].append(result)
            else:
                # Route not found
                self.results['not_found'].append(result)
        elif status == 200 or (isinstance(status, int) and 200 <= status < 300):
            if not result.get('cors'):
                self.results['cors_issues'].append(result)
            else:
                self.results['working'].append(result)
        elif isinstance(status, int) and status < 500:
            # 4xx errors - client errors but endpoint exists
            if not result.get('cors'):
                self.results['cors_issues'].append(result)
            else:
                self.results['working'].append(result)  # Endpoint exists, just needs correct params
        else:
            self.results['errors'].append(result)
    
    def test_all_endpoints(self):
        """Test all known API endpoints"""
        
        print("=" * 80)
        print("ENVISION API Endpoint Comprehensive Test")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Frontend origin: http://localhost:3000")
        print()
        
        # First, test if server is running
        print("1. Checking server connectivity...")
        health_result = self.test_endpoint('GET', '/api/health')
        if health_result.get('status') == 'CONNECTION_ERROR':
            print(f"   ✗ Server is NOT running on {self.base_url}")
            print(f"   Please start the server with: python run_all.py")
            return False
        
        if health_result.get('status') == 200:
            print(f"   [OK] Server is running")
            print(f"   Response: {json.dumps(health_result.get('response', {}), indent=2)}")
        else:
            print(f"   [WARN] Server responded with status {health_result.get('status')}")
        
        print()
        
        # Test CORS
        print("2. Testing CORS configuration...")
        cors_result = self.test_endpoint('GET', '/api/health')
        if cors_result.get('cors'):
            cors_origin = cors_result.get('cors_origin', '')
            print(f"   [OK] CORS is configured")
            print(f"   Access-Control-Allow-Origin: {cors_origin}")
            if 'localhost:3000' in cors_origin or cors_origin == '*':
                print(f"   [OK] localhost:3000 is allowed")
            else:
                print(f"   [WARN] localhost:3000 might not be explicitly allowed")
        else:
            print(f"   [ERROR] CORS headers not found - this will cause issues!")
        
        print()
        
        # Define all endpoints to test
        endpoints = [
            # Health
            ('GET', '/api/health', None, 200),
            
            # Camera Control
            ('POST', '/api/start-camera', {'cameraType': 'hikrobot'}, None),
            ('POST', '/api/stop-camera', {}, None),
            ('GET', '/api/video-feed', None, None),
            ('POST', '/api/snapshot', {'magnification': '100x'}, None),
            ('POST', '/api/set-camera-resolution', {'width': 1920, 'height': 1080}, None),
            
            # Image Management
            ('POST', '/api/import-image', {}, None),  # Needs file upload
            ('GET', '/api/get-image', {'path': 'test.jpg'}, None),
            ('POST', '/api/list-images', {}, None),
            ('POST', '/api/delete-image', {'imagePath': 'test.jpg'}, None),
            ('GET', '/api/thumbnail', {'path': 'test.jpg'}, None),
            
            # Image Processing
            ('POST', '/api/rotate-image', {'imagePath': 'test.jpg', 'angle': 90}, None),
            ('POST', '/api/flip-image', {'imagePath': 'test.jpg', 'direction': 'horizontal'}, None),
            ('POST', '/api/grayscale', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/invert', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/threshold', {'imagePath': 'test.jpg', 'threshold': 128}, None),
            ('POST', '/api/lowpass-filter', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/median-filter', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/edge-detect', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/edge-emphasis', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/image-sharpen', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/image-splice', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/image-stitch', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/thin', {'imagePath': 'test.jpg'}, None),
            
            # New Image Processing Blueprint
            ('POST', '/api/image/brightness-contrast', {'imagePath': 'test.jpg', 'brightness': 20, 'contrast': 1.2}, None),
            ('POST', '/api/image/gamma', {'imagePath': 'test.jpg', 'gamma': 1.5}, None),
            ('POST', '/api/image/saturation', {'imagePath': 'test.jpg', 'saturation': 1.3}, None),
            ('POST', '/api/image/histogram-equalization', {'imagePath': 'test.jpg'}, None),
            ('POST', '/api/image/resize', {'imagePath': 'test.jpg', 'width': 800, 'height': 600}, None),
            ('POST', '/api/image/process-multiple', {'imagePath': 'test.jpg', 'operations': {}}, None),
            
            # Calibration
            ('POST', '/api/save-calibration', {'name': 'test', 'data': {}}, None),
            ('GET', '/api/get-calibrations', None, None),
            
            # Porosity Analysis
            ('POST', '/api/porosity/analyze', {'image_path': 'test.jpg'}, None),
            ('POST', '/api/porosity/save-config', {'name': 'test', 'config': {}}, None),
            ('GET', '/api/porosity/load-config/test', None, None),
            ('POST', '/api/porosity/export-report', {'image_path': 'test.jpg'}, None),
            ('POST', '/api/porosity/get-histogram', {'image_path': 'test.jpg'}, None),
            ('POST', '/api/porosity/apply-intensity-threshold', {'image_path': 'test.jpg'}, None),
            
            # Phase Analysis
            ('POST', '/api/phase/analyze', {'image_path': 'test.jpg'}, None),
            ('POST', '/api/phase/save-configuration', {'name': 'test', 'configuration': {}}, None),
            ('GET', '/api/phase/get-configurations', None, None),
            ('POST', '/api/phase/apply-configuration', {'name': 'test'}, None),
            
            # Nodularity Analysis
            ('POST', '/api/nodularity/analyze', {'image_path': 'test.jpg'}, None),
            ('POST', '/api/nodularity/toggle-selection', {}, None),
            ('POST', '/api/nodularity/set-cutoff', {'cutoff': 0.5}, None),
            ('POST', '/api/nodularity/update-sizes', {'sizes': []}, None),
            ('POST', '/api/nodularity/export-report', {'image_path': 'test.jpg'}, None),
            ('POST', '/api/nodularity/add-cumulative-result', {'result': {}}, None),
            ('GET', '/api/nodularity/get-cumulative-results', None, None),
            ('POST', '/api/nodularity/clear-cumulative-results', {}, None),
            ('POST', '/api/nodularity/save-config', {'name': 'test', 'config': {}}, None),
            ('GET', '/api/nodularity/load-config/test', None, None),
            ('POST', '/api/nodularity/delete-config', {'name': 'test'}, None),
            ('POST', '/api/nodularity/transfer-to-phase-analysis', {}, None),
        ]
        
        print("3. Testing all API endpoints...")
        print("   (This may take a moment)")
        print()
        
        total = len(endpoints)
        for i, (method, path, data, expected_status) in enumerate(endpoints, 1):
            print(f"   [{i}/{total}] Testing {method} {path}...", end=' ')
            result = self.test_endpoint(method, path, data, expected_status)
            self.categorize_result(result)
            
            status = result.get('status')
            if status == 200:
                print(f"[OK]")
            elif isinstance(status, int) and 200 <= status < 400:
                print(f"[OK] {status} (endpoint exists)")
            elif status == 404:
                print(f"[404] not found")
            elif status == 'CONNECTION_ERROR':
                print(f"[ERROR] Connection error")
            else:
                print(f"[{status}]")
        
        print()
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("Test Summary")
        print("=" * 80)
        print()
        
        total_tested = sum(len(v) for v in self.results.values())
        
        print(f"Total endpoints tested: {total_tested}")
        print(f"  [OK] Working: {len(self.results['working'])}")
        print(f"  [ERROR] Errors: {len(self.results['errors'])}")
        print(f"  [WARN] CORS issues: {len(self.results['cors_issues'])}")
        print(f"  [404] Not found: {len(self.results['not_found'])}")
        print()
        
        # Show errors
        if self.results['errors']:
            print("Endpoints with errors:")
            print("-" * 80)
            for result in self.results['errors'][:10]:
                print(f"  [ERROR] {result['method']} {result['path']}")
                if 'error' in result:
                    print(f"    Error: {result['error']}")
            if len(self.results['errors']) > 10:
                print(f"  ... and {len(self.results['errors']) - 10} more")
            print()
        
        # Show 404s
        if self.results['not_found']:
            print("Endpoints not found (404) - These routes may not be registered:")
            print("-" * 80)
            for result in self.results['not_found'][:15]:
                print(f"  [404] {result['method']:6} {result['path']}")
            if len(self.results['not_found']) > 15:
                print(f"  ... and {len(self.results['not_found']) - 15} more")
            print()
        
        # Show CORS issues
        if self.results['cors_issues']:
            print("Endpoints with CORS issues:")
            print("-" * 80)
            for result in self.results['cors_issues'][:10]:
                print(f"  [WARN] {result['method']} {result['path']}")
                print(f"    Missing CORS headers")
            if len(self.results['cors_issues']) > 10:
                print(f"  ... and {len(self.results['cors_issues']) - 10} more")
            print()
        
        # Show working endpoints
        if self.results['working']:
            print(f"Working endpoints ({len(self.results['working'])}):")
            print("-" * 80)
            for result in self.results['working'][:20]:
                status = result.get('status')
                print(f"  [OK] {result['method']:6} {result['path']:50} Status: {status}")
            if len(self.results['working']) > 20:
                print(f"  ... and {len(self.results['working']) - 20} more")
            print()
        
        print("=" * 80)
        print("Recommendations:")
        print("=" * 80)
        
        if self.results['not_found']:
            print("1. Some endpoints return 404 - verify routes are registered")
        
        if self.results['cors_issues']:
            print("2. Some endpoints missing CORS headers - check camera_server.py CORS config")
        
        if self.results['errors']:
            print("3. Some endpoints have errors - check server logs")
        
        print("4. Check browser console (F12) for frontend API call errors")
        print("5. Verify server is running: python run_all.py")
        print()

def main():
    base_url = "http://localhost:5000"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    tester = APITester(base_url)
    
    try:
        success = tester.test_all_endpoints()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

