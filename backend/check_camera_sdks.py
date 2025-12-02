"""
Utility script to check camera SDK availability and DLL paths
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from camera_config import (
    check_camera_sdk_availability,
    find_dll,
    add_dll_paths,
    DLL_PATHS,
    get_service_config
)

# Try to import find_mvs_dll if available
try:
    from find_mvs_dll import find_mvs_dll
    HAS_FIND_DLL = True
except ImportError:
    HAS_FIND_DLL = False

def main():
    print("=" * 60)
    print("ENVISION Camera SDK Checker")
    print("=" * 60)
    print()
    
    # Check SDK availability
    print("Checking Camera SDK Availability...")
    print("-" * 60)
    availability = check_camera_sdk_availability()
    
    for camera_type, is_available in availability.items():
        status = "✓ Available" if is_available else "✗ Not Available"
        print(f"{camera_type.upper():12} : {status}")
    
    print()
    
    # Check DLL files
    print("Checking DLL Files...")
    print("-" * 60)
    platform = 'windows' if sys.platform == 'win32' else 'linux'
    
    for camera_type in ['ids', 'mshot', 'hikrobot']:
        print(f"\n{camera_type.upper()}:")
        dll_files = DLL_PATHS[camera_type].get('dll_files', [])
        paths = DLL_PATHS[camera_type].get(platform, [])
        
        found_any = False
        for dll_file in dll_files:
            if platform == 'windows' and not dll_file.endswith('.dll'):
                continue
            if platform == 'linux' and not dll_file.endswith('.so'):
                continue
                
            dll_path = find_dll(camera_type, dll_file)
            if dll_path:
                print(f"  ✓ Found: {dll_path}")
                found_any = True
            else:
                print(f"  ✗ Not found: {dll_file}")
                print(f"    Searched in:")
                for path in paths:
                    exists = "✓" if os.path.exists(path) else "✗"
                    print(f"      {exists} {path}")
        
        # For Hikrobot, also try to find DLL if not found in configured paths
        if not found_any and camera_type == 'hikrobot' and HAS_FIND_DLL:
            print(f"\n  Searching system-wide for {dll_files[0]}...")
            all_locations = find_mvs_dll()
            if all_locations:
                print(f"  ✓ Found in other locations:")
                for loc in all_locations[:3]:  # Show first 3
                    print(f"      - {loc}")
                if len(all_locations) > 3:
                    print(f"      ... and {len(all_locations) - 3} more")
                print(f"\n  💡 Tip: Run 'python setup_mvs_dll.py' to copy DLL to configured location")
        
        if not found_any and camera_type == 'hikrobot':
            print(f"  ⚠ No DLL files found for {camera_type}")
            print(f"  💡 Run 'python find_mvs_dll.py' to search for DLL")
            print(f"  💡 Run 'python setup_mvs_dll.py' to set up DLL")
    
    print()
    
    # Show service configuration
    print("Service Configuration...")
    print("-" * 60)
    config = get_service_config()
    for key, value in config.items():
        print(f"{key:20} : {value}")
    
    print()
    print("=" * 60)
    print("Check complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

