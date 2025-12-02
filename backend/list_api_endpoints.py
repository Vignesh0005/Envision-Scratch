"""
Simple API Endpoint Lister
Lists all API endpoints without requiring server to be running
"""

import sys
import os

def main():
    print("=" * 80)
    print("ENVISION API Endpoints List")
    print("=" * 80)
    print()
    
    # Read camera_server.py to extract routes
    print("Scanning camera_server.py for API endpoints...")
    print("-" * 80)
    
    api_endpoints = []
    
    try:
        with open('camera_server.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if '@app.route' in line:
                # Extract route path and methods
                route_line = line.strip()
                # Get next few lines for context
                context = ''.join(lines[i:i+3])
                
                # Extract path
                if "'" in route_line:
                    path = route_line.split("'")[1] if "'" in route_line else route_line.split('"')[1]
                else:
                    path = 'unknown'
                
                # Extract methods
                if 'methods=' in route_line:
                    if '[' in route_line:
                        methods_part = route_line.split('[')[1].split(']')[0]
                        methods = [m.strip().strip("'\"") for m in methods_part.split(',')]
                    else:
                        methods = ['GET']
                else:
                    methods = ['GET']
                
                if path.startswith('/api/'):
                    api_endpoints.append({
                        'path': path,
                        'methods': methods
                    })
    except Exception as e:
        print(f"Error reading camera_server.py: {e}")
        print("Showing common endpoints instead...")
        api_endpoints = get_common_endpoints()
    
    # Also check api_image_processing.py
    try:
        with open('api_image_processing.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if '@image_processing_bp.route' in line:
                route_line = line.strip()
                if "'" in route_line:
                    path = route_line.split("'")[1] if "'" in route_line else route_line.split('"')[1]
                else:
                    path = 'unknown'
                
                if 'methods=' in route_line:
                    if '[' in route_line:
                        methods_part = route_line.split('[')[1].split(']')[0]
                        methods = [m.strip().strip("'\"") for m in methods_part.split(',')]
                    else:
                        methods = ['GET']
                else:
                    methods = ['GET']
                
                if path.startswith('/api/'):
                    api_endpoints.append({
                        'path': path,
                        'methods': methods
                    })
    except Exception as e:
        print(f"Note: Could not read api_image_processing.py: {e}")
    
    # Remove duplicates
    seen = set()
    unique_endpoints = []
    for ep in api_endpoints:
        key = (ep['path'], tuple(sorted(ep['methods'])))
        if key not in seen:
            seen.add(key)
            unique_endpoints.append(ep)
    
    # Sort by path
    unique_endpoints.sort(key=lambda x: x['path'])
    
    print(f"\nFound {len(unique_endpoints)} API endpoints:\n")
    
    # Group by category
    categories = {
        'Camera Control': [],
        'Image Management': [],
        'Image Processing': [],
        'Analysis': [],
        'Calibration': [],
        'Health': []
    }
    
    for ep in unique_endpoints:
        path = ep['path']
        if 'camera' in path or 'video' in path or 'snapshot' in path:
            categories['Camera Control'].append(ep)
        elif 'image' in path and ('import' in path or 'get-image' in path or 'list' in path or 'delete' in path):
            categories['Image Management'].append(ep)
        elif 'image' in path or 'filter' in path or 'rotate' in path or 'flip' in path:
            categories['Image Processing'].append(ep)
        elif 'porosity' in path or 'phase' in path or 'nodularity' in path:
            categories['Analysis'].append(ep)
        elif 'calibration' in path:
            categories['Calibration'].append(ep)
        elif 'health' in path:
            categories['Health'].append(ep)
        else:
            categories['Image Processing'].append(ep)
    
    for category, endpoints in categories.items():
        if endpoints:
            print(f"\n{category}:")
            print("-" * 80)
            for ep in endpoints:
                methods_str = ', '.join(ep['methods'])
                print(f"  {methods_str:20} {ep['path']}")
    
    print()
    print("=" * 80)
    print("Quick Test Commands:")
    print("=" * 80)
    print()
    print("# Test if server is running:")
    print("curl http://localhost:5000/api/health")
    print()
    print("# Test CORS:")
    print("curl -H 'Origin: http://localhost:3000' http://localhost:5000/api/health")
    print()
    print("# Start server:")
    print("python run_all.py")
    print()
    print("=" * 80)

def get_common_endpoints():
    """Return common endpoints if file reading fails"""
    return [
        {'path': '/api/health', 'methods': ['GET']},
        {'path': '/api/start-camera', 'methods': ['POST']},
        {'path': '/api/stop-camera', 'methods': ['POST']},
        {'path': '/api/video-feed', 'methods': ['GET']},
        {'path': '/api/snapshot', 'methods': ['POST']},
        {'path': '/api/import-image', 'methods': ['POST']},
        {'path': '/api/get-image', 'methods': ['GET']},
    ]

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

