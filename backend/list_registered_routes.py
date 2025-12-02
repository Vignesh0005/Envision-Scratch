"""
List all registered Flask routes
"""

try:
    from camera_server import app
    
    print("=" * 80)
    print("Registered Flask Routes")
    print("=" * 80)
    print()
    
    api_routes = []
    other_routes = []
    
    for rule in app.url_map.iter_rules():
        route_info = {
            'path': str(rule),
            'methods': list(rule.methods - {'OPTIONS', 'HEAD'}),
            'endpoint': rule.endpoint
        }
        
        if str(rule).startswith('/api/'):
            api_routes.append(route_info)
        else:
            other_routes.append(route_info)
    
    print(f"API Routes ({len(api_routes)}):")
    print("-" * 80)
    for route in sorted(api_routes, key=lambda x: x['path']):
        methods = ', '.join(route['methods'])
        print(f"  {methods:20} {route['path']:50} ({route['endpoint']})")
    
    print()
    print(f"Other Routes ({len(other_routes)}):")
    print("-" * 80)
    for route in sorted(other_routes, key=lambda x: x['path']):
        methods = ', '.join(route['methods'])
        print(f"  {methods:20} {route['path']}")
    
    print()
    print("=" * 80)
    print(f"Total API routes: {len(api_routes)}")
    print("=" * 80)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

