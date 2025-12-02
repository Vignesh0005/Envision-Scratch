"""
Check if IDS uEye SDK is properly installed
"""

import os
import sys
from pathlib import Path

def find_ueye_dll():
    """Find ueye_api.dll"""
    dll_name = "ueye_api.dll"
    found_locations = []
    
    # Common IDS SDK installation paths
    search_paths = [
        r"C:\Program Files\IDS\uEye\Develop\Bin64",
        r"C:\Program Files (x86)\IDS\uEye\Develop\Bin64",
        r"C:\Program Files\IDS\uEye\Develop\Bin",
        r"C:\Program Files (x86)\IDS\uEye\Develop\Bin",
        str(Path(__file__).parent / "libs" / "ids"),
    ]
    
    print("Searching for ueye_api.dll...")
    print("=" * 60)
    
    for path in search_paths:
        if os.path.exists(path):
            dll_path = os.path.join(path, dll_name)
            if os.path.exists(dll_path):
                found_locations.append(dll_path)
                print(f"✓ Found: {dll_path}")
            else:
                # Check subdirectories
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
        print(f"\n✓ Found {len(found_locations)} location(s):")
        for i, location in enumerate(found_locations, 1):
            print(f"  {i}. {location}")
        
        # Test pyueye import
        print("\n" + "=" * 60)
        print("Testing pyueye import...")
        print("=" * 60)
        
        # Set DLL path if found
        dll_dir = os.path.dirname(found_locations[0])
        os.environ['PYUEYE_DLL_PATH'] = dll_dir
        print(f"Set PYUEYE_DLL_PATH={dll_dir}")
        
        try:
            import pyueye
            print("✓ pyueye imported successfully!")
            print("✓ IDS uEye SDK is ready to use")
            return True
        except Exception as e:
            print(f"✗ Error importing pyueye: {e}")
            print("\nTry setting environment variable:")
            print(f"  set PYUEYE_DLL_PATH={dll_dir}")
            return False
    else:
        print("\n✗ ueye_api.dll not found")
        print("\nTo use IDS cameras, you need to:")
        print("1. Download IDS uEye SDK from:")
        print("   https://en.ids-imaging.com/downloads.html")
        print("2. Install the SDK")
        print("3. The DLL should be in:")
        print("   C:\\Program Files\\IDS\\uEye\\Develop\\Bin64\\")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IDS uEye SDK Checker")
    print("=" * 60)
    print()
    
    find_ueye_dll()
    
    print("\n" + "=" * 60)
    print("Note: pyueye package is installed")
    print("You just need the IDS uEye SDK DLL files")
    print("=" * 60)

