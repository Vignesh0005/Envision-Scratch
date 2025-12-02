"""
Check what routes are actually registered in Flask app
"""

import sys
import os

# Suppress stdout/stderr during import
old_stdout = sys.stdout
old_stderr = sys.stderr
try:
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    from camera_server import app
finally:
    sys.stdout = old_stdout
    sys.stderr = old_stderr

print("=" * 80)
print("Registered Flask Routes")
print("=" * 80)
print()

api_routes = []
for rule in app.url_map.iter_rules():
    if str(rule).startswith('/api/'):
        methods = list(rule.methods - {'OPTIONS', 'HEAD'})
        api_routes.append({
            'path': str(rule),
            'methods': methods,
            'endpoint': rule.endpoint
        })

print(f"Total API Routes Registered: {len(api_routes)}")
print()
print("All Registered API Routes:")
print("-" * 80)

for route in sorted(api_routes, key=lambda x: x['path']):
    methods_str = ', '.join(route['methods'])
    print(f"  {methods_str:20} {route['path']:50}")

print()
print("=" * 80)

# Check for specific missing routes
missing_routes = [
    '/api/rotate-image',
    '/api/flip-image',
    '/api/grayscale',
    '/api/invert',
    '/api/threshold',
    '/api/image/brightness-contrast',
    '/api/image/gamma',
]

print("\nChecking for specific routes:")
print("-" * 80)
for route_path in missing_routes:
    found = any(r['path'] == route_path for r in api_routes)
    status = "[FOUND]" if found else "[MISSING]"
    print(f"  {status} {route_path}")

print()

