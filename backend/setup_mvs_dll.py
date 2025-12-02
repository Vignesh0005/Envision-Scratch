"""
Setup script to help configure MvCameraControl.dll
Run this if you already have the DLL downloaded
"""

import os
import shutil
import sys
from pathlib import Path
from find_mvs_dll import find_mvs_dll

def setup_dll():
    """Help user set up the MVS DLL"""
    print("=" * 60)
    print("MVS DLL Setup Helper")
    print("=" * 60)
    print()
    
    # Find existing DLL
    print("Step 1: Finding existing MvCameraControl.dll...")
    locations = find_mvs_dll()
    
    if not locations:
        print("\n" + "=" * 60)
        print("DLL Not Found Automatically")
        print("=" * 60)
        print("\nPlease provide the path to your MvCameraControl.dll:")
        dll_path = input("Enter full path to MvCameraControl.dll: ").strip().strip('"')
        
        if os.path.exists(dll_path) and dll_path.endswith('.dll'):
            locations = [dll_path]
        else:
            print("✗ Invalid path or file not found")
            return False
    
    # Recommend best location
    source_dll = locations[0]
    target_dir = Path(__file__).parent / 'libs' / 'hikrobot'
    target_dir.mkdir(parents=True, exist_ok=True)
    target_dll = target_dir / 'MvCameraControl.dll'
    
    print("\n" + "=" * 60)
    print("Step 2: Setting up DLL")
    print("=" * 60)
    print(f"Source: {source_dll}")
    print(f"Target: {target_dll}")
    
    # Check if already in target
    if target_dll.exists():
        print(f"\n✓ DLL already exists at target location")
        response = input("Copy anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping copy. Using existing DLL.")
            return True
    
    # Copy DLL
    try:
        print(f"\nCopying DLL to {target_dll}...")
        shutil.copy2(source_dll, target_dll)
        print("✓ DLL copied successfully!")
    except Exception as e:
        print(f"✗ Error copying DLL: {e}")
        print(f"\nYou can manually copy:")
        print(f"  From: {source_dll}")
        print(f"  To:   {target_dll}")
        return False
    
    # Verify
    print("\n" + "=" * 60)
    print("Step 3: Verifying Setup")
    print("=" * 60)
    
    from camera_config import find_dll, check_camera_sdk_availability
    
    dll_path = find_dll('hikrobot')
    if dll_path:
        print(f"✓ DLL found by system: {dll_path}")
    else:
        print("⚠ DLL not found by system (may need to restart Python)")
    
    availability = check_camera_sdk_availability()
    if availability.get('hikrobot', False):
        print("✓ Hikrobot SDK is available!")
        return True
    else:
        print("⚠ Hikrobot SDK not available yet")
        print("  Try running: python check_camera_sdks.py")
        return False


if __name__ == "__main__":
    try:
        success = setup_dll()
        
        print("\n" + "=" * 60)
        if success:
            print("Setup Complete!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Run: python check_camera_sdks.py")
            print("2. Test camera: python start_server.py")
        else:
            print("Setup Incomplete")
            print("=" * 60)
            print("\nPlease:")
            print("1. Ensure DLL is accessible")
            print("2. Check file permissions")
            print("3. Verify DLL architecture (64-bit)")
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

