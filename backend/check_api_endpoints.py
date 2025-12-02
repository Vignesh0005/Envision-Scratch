"""
API Endpoint Checker and Tester
Checks all API endpoints for connectivity and CORS issues
"""

import sys
import json

def check_imports():
    """Check if required modules are available"""
    missing = []
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    app = None
    try:
        # Try to import app, but don't fail if it doesn't work
        import sys
        import os
        # Suppress stdout/stderr during import to avoid log file issues
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            from camera_server import app
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    except Exception as e:
        print(f"Note: Could not import camera_server (this is okay): {e}")
        print("Will use manual endpoint list instead")
    
    return app, missing

def get_all_routes(app):
    """Get all registered routes from Flask app"""
    if app is None:
        return []
    
    routes = []
    try:
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods - {'OPTIONS', 'HEAD'}),
                'path': str(rule)
            })
    except Exception as e:
        print(f"Error getting routes: {e}")
    
    return routes

def test_endpoint_simple(base_url, path, method='GET'):
    """Test an API endpoint (simple version)"""
    try:
        import requests
    except ImportError:
        return {'error': 'requests library not installed'}
    
    url = f"{base_url}{path}"
    try:
        if method == 'GET':
            response = requests.get(url, timeout=3)
        elif method == 'POST':
            response = requests.post(url, json={}, timeout=3)
        else:
            return {'error': f'Method {method} not supported'}
        
        return {
            'url': url,
            'method': method,
            'status': response.status_code,
            'cors': 'Access-Control-Allow-Origin' in response.headers,
            'content_type': response.headers.get('Content-Type', 'N/A'),
            'ok': response.status_code < 500
        }
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        return {
            'url': url,
            'method': method,
            'status': 'CONNECTION_REFUSED',
            'error': 'Server not running'
        }
    except Exception as e:
        return {
            'url': url,
            'method': method,
            'status': 'ERROR',
            'error': str(e)
        }

def main():
    print("=" * 80)
    print("ENVISION API Endpoint Checker")
    print("=" * 80)
    print()
    
    # Check imports
    app, missing = check_imports()
    
    if missing:
        print("⚠ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print()
        print("Install with: pip install " + " ".join(missing))
        print()
        if 'requests' in missing:
            print("Continuing with endpoint listing only (no connectivity tests)...")
            print()
    
    # List all endpoints
    print("1. Listing all API endpoints...")
    print("-" * 80)
    
    if app:
        try:
            routes = get_all_routes(app)
            api_routes = [r for r in routes if r['path'].startswith('/api/')]
            
            print(f"Found {len(api_routes)} API endpoints:")
            print()
            
            for route in sorted(api_routes, key=lambda x: x['path']):
                methods_str = ', '.join(route['methods'])
                print(f"  {methods_str:20} {route['path']}")
        except Exception as e:
            print(f"Error getting routes: {e}")
            print("Run 'python list_api_endpoints.py' for full list")
    else:
        # Use the list script instead
        print("For full endpoint list, run: python list_api_endpoints.py")
        print()
        print("Common endpoints:")
        common_endpoints = [
            ('GET', '/api/health'),
            ('POST', '/api/start-camera'),
            ('POST', '/api/stop-camera'),
            ('GET', '/api/video-feed'),
            ('POST', '/api/snapshot'),
            ('POST', '/api/import-image'),
        ]
        for method, path in common_endpoints:
            print(f"  {method:20} {path}")
    
    print()
    print("-" * 80)
    print()
    
    # Test connectivity if requests is available
    base_url = "http://localhost:5000"
    
    try:
        import requests
        print("2. Testing server connectivity...")
        print("-" * 80)
        
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print(f"   ✓ Server is running on {base_url}")
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"   Response: {response.text[:100]}")
            else:
                print(f"   ⚠ Server responded with status {response.status_code}")
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
            print(f"   ✗ Server is NOT running on {base_url}")
            print(f"   Please start the server with: python run_all.py")
            print()
            return
        except Exception as e:
            print(f"   ✗ Error connecting: {e}")
            print()
            return
        
        print()
        
        # Check CORS
        print("3. Checking CORS configuration...")
        print("-" * 80)
        
        try:
            response = requests.get(
                f"{base_url}/api/health",
                headers={'Origin': 'http://localhost:3000'},
                timeout=2
            )
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')
            
            print(f"   Access-Control-Allow-Origin: {cors_origin or 'NOT SET'}")
            print(f"   Access-Control-Allow-Methods: {cors_methods or 'NOT SET'}")
            
            if cors_origin:
                if 'localhost:3000' in cors_origin or cors_origin == '*':
                    print(f"   ✓ localhost:3000 is allowed")
                else:
                    print(f"   ⚠ localhost:3000 might not be allowed")
            else:
                print(f"   ⚠ No CORS header found - this may cause issues!")
        except Exception as e:
            print(f"   ✗ Error checking CORS: {e}")
        
        print()
        
        # Test a few key endpoints
        print("4. Testing key endpoints...")
        print("-" * 80)
        
        key_endpoints = [
            ('GET', '/api/health'),
            ('POST', '/api/start-camera'),
            ('GET', '/api/video-feed'),
        ]
        
        for method, path in key_endpoints:
            result = test_endpoint_simple(base_url, path, method)
            if 'error' in result:
                if result['error'] == 'Server not running':
                    print(f"   ✗ {method} {path}: Server not running")
                else:
                    print(f"   ⚠ {method} {path}: {result['error']}")
            else:
                status = result.get('status')
                cors = result.get('cors', False)
                if status == 200:
                    print(f"   ✓ {method} {path}: OK (CORS: {'✓' if cors else '✗'})")
                elif status < 500:
                    print(f"   ⚠ {method} {path}: Status {status} (CORS: {'✓' if cors else '✗'})")
                else:
                    print(f"   ✗ {method} {path}: Error {status}")
        
    except ImportError:
        print("2. Skipping connectivity tests (requests not installed)")
        print("   Install with: pip install requests")
    
    print()
    print("=" * 80)
    print("Check complete!")
    print("=" * 80)
    print()
    print("Troubleshooting:")
    print("1. If server not running: python run_all.py")
    print("2. If CORS issues: Check camera_server.py CORS configuration")
    print("3. If blank screens: Check browser console (F12) for errors")
    print("4. Check Network tab in browser DevTools for failed requests")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
