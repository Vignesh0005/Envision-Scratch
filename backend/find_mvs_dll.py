"""
Find MvCameraControl.dll on the system
Helps locate the DLL if it's already downloaded
"""

import os
import sys
from pathlib import Path

def find_mvs_dll():
    """Search for MvCameraControl.dll in common locations"""
    dll_name = "MvCameraControl.dll"
    found_locations = []
    
    # Common installation paths
    search_paths = [
        # Standard MVS SDK installation paths
        r"C:\Program Files\MVS\Development\Bin\x64",
        r"C:\Program Files (x86)\MVS\Development\Bin\x64",
        r"C:\Program Files\MVS\Development\Bin\Win64",
        r"C:\Program Files (x86)\MVS\Development\Bin\Win64",
        
        # Runtime paths
        r"C:\Program Files (x86)\Common Files\MVS\Runtime\Win64_x64",
        r"C:\Program Files\Common Files\MVS\Runtime\Win64_x64",
        
        # Sample/Python paths
        r"C:\Program Files\MVS\Development\Samples\Python\MvImport",
        r"C:\Program Files (x86)\MVS\Development\Samples\Python\MvImport",
        
        # Project directories
        str(Path(__file__).parent),  # backend directory
        str(Path(__file__).parent.parent / "MvImport"),  # MvImport directory
        str(Path(__file__).parent / "libs" / "hikrobot"),
        
        # Current directory and subdirectories
        os.getcwd(),
        str(Path(__file__).parent.parent),
    ]
    
    # Check alternative drives
    for drive in ['C:', 'D:', 'E:', 'F:', 'G:']:
        if os.path.exists(drive):
            alt_paths = [
                os.path.join(drive, 'Program Files', 'MVS', 'Development', 'Bin', 'x64'),
                os.path.join(drive, 'Program Files (x86)', 'MVS', 'Development', 'Bin', 'x64'),
                os.path.join(drive, 'Program Files', 'MVS', 'Development', 'Bin', 'Win64'),
                os.path.join(drive, 'Program Files (x86)', 'MVS', 'Development', 'Bin', 'Win64'),
                os.path.join(drive, 'Program Files (x86)', 'Common Files', 'MVS', 'Runtime', 'Win64_x64'),
                os.path.join(drive, 'MVS', 'Development', 'Bin', 'x64'),
                os.path.join(drive, 'MVS', 'Development', 'Bin', 'Win64'),
            ]
            search_paths.extend(alt_paths)
    
    # Search in each path
    print("Searching for MvCameraControl.dll...")
    print("=" * 60)
    
    for path in search_paths:
        if os.path.exists(path):
            dll_path = os.path.join(path, dll_name)
            if os.path.exists(dll_path):
                found_locations.append(dll_path)
                print(f"✓ Found: {dll_path}")
            else:
                # Also check subdirectories
                try:
                    for root, dirs, files in os.walk(path):
                        if dll_name in files:
                            full_path = os.path.join(root, dll_name)
                            if full_path not in found_locations:
                                found_locations.append(full_path)
                                print(f"✓ Found: {full_path}")
                except PermissionError:
                    pass
    
    print("=" * 60)
    
    if found_locations:
        print(f"\nFound {len(found_locations)} location(s):")
        for i, location in enumerate(found_locations, 1):
            print(f"  {i}. {location}")
        
        # Recommend best location
        recommended = found_locations[0]
        print(f"\n✓ Recommended location: {recommended}")
        print(f"  Directory: {os.path.dirname(recommended)}")
        
        # Check if it's in a configured path
        from camera_config import DLL_PATHS
        hikrobot_paths = DLL_PATHS['hikrobot']['windows']
        in_configured = any(recommended.startswith(p) for p in hikrobot_paths if os.path.exists(p))
        
        if in_configured:
            print("  ✓ This location is already in the configuration")
        else:
            print("  ⚠ This location is NOT in the configuration")
            print("  You may want to add it to camera_config.py or copy DLL to a configured location")
        
        return found_locations
    else:
        print("\n✗ MvCameraControl.dll not found in common locations")
        print("\nPlease:")
        print("1. Check if the DLL is in a custom location")
        print("2. Copy it to one of these locations:")
        print(f"   - {Path(__file__).parent / 'libs' / 'hikrobot'}")
        print(f"   - {Path(__file__).parent}")
        print("3. Or add your DLL location to camera_config.py")
        return []


def verify_dll_accessibility(dll_path):
    """Verify DLL can be loaded"""
    try:
        import ctypes
        dll = ctypes.WinDLL(dll_path)
        print(f"✓ DLL is accessible and can be loaded: {dll_path}")
        return True
    except Exception as e:
        print(f"✗ DLL cannot be loaded: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MVS DLL Finder - ENVISION")
    print("=" * 60)
    print()
    
    locations = find_mvs_dll()
    
    if locations:
        print("\n" + "=" * 60)
        print("Verifying DLL Accessibility")
        print("=" * 60)
        
        for location in locations:
            verify_dll_accessibility(location)
        
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. If DLL is found, run: python check_camera_sdks.py")
        print("2. If DLL is not in configured paths, you can:")
        print("   - Copy DLL to: backend/libs/hikrobot/")
        print("   - Or add the path to camera_config.py")
        print("3. Test camera connection after verification")
    else:
        print("\n" + "=" * 60)
        print("Troubleshooting:")
        print("=" * 60)
        print("1. Ensure MVS SDK is installed")
        print("2. Check if DLL is in a custom location")
        print("3. Copy DLL to backend/libs/hikrobot/ if needed")
        print("4. Verify DLL architecture matches Python (64-bit)")

