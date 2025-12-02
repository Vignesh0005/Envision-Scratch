"""
Configuration file for camera service DLL paths and settings
Integrated with ENVISION project
"""

import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = Path(__file__).parent

# DLL/Library paths configuration
DLL_PATHS = {
    'ids': {
        'windows': [
            r'C:\Program Files\IDS\uEye\Develop\Bin64',
            r'C:\Program Files (x86)\IDS\uEye\Develop\Bin64',
            str(BASE_DIR / 'libs' / 'ids'),
        ],
        'linux': [
            '/usr/lib',
            '/usr/local/lib',
            str(BASE_DIR / 'libs' / 'ids'),
        ],
        'dll_files': [
            'ueye_api.dll',  # Windows
            'libueye_api.so',  # Linux
        ]
    },
    'mshot': {
        'windows': [
            r'C:\Program Files\Mshot',
            r'C:\Program Files (x86)\Mshot',
            str(BASE_DIR / 'libs' / 'mshot'),
        ],
        'linux': [
            '/usr/lib',
            '/usr/local/lib',
            str(BASE_DIR / 'libs' / 'mshot'),
        ],
        'dll_files': [
            'mshot.dll',  # Windows
            'libmshot.so',  # Linux
        ]
    },
    'hikrobot': {
        'windows': [
            r'C:\Program Files\MVS\Development\Bin\x64',
            r'C:\Program Files (x86)\MVS\Development\Bin\x64',
            r'C:\Program Files\MVS\Development\Bin\Win64',
            r'C:\Program Files (x86)\MVS\Development\Bin\Win64',
            r'C:\Program Files (x86)\Common Files\MVS\Runtime\Win64_x64',  # Common runtime path
            r'C:\Program Files\Common Files\MVS\Runtime\Win64_x64',
            r'C:\Program Files\MVS\Development\Samples\Python\MvImport',
            r'C:\Program Files (x86)\MVS\Development\Samples\Python\MvImport',
            str(BASE_DIR / 'libs' / 'hikrobot'),
            str(BASE_DIR.parent / 'MvImport'),  # ENVISION's existing MvImport directory
            str(BASE_DIR),  # Current backend directory
        ],
        'linux': [
            '/usr/lib',
            '/usr/local/lib',
            str(BASE_DIR / 'libs' / 'hikrobot'),
        ],
        'dll_files': [
            'MvCameraControl.dll',  # Windows
            'libMvCameraControl.so',  # Linux
        ]
    }
}

# Camera service settings
SERVICE_CONFIG = {
    'host': 'localhost',
    'port': 8765,
    'max_connections': 10,
    'frame_rate': 30,
    'jpeg_quality': 90,
    'buffer_size': 1024 * 1024,  # 1MB
}

# Image processing defaults
IMAGE_PROCESSING_DEFAULTS = {
    'rotation': 0,
    'flip_horizontal': False,
    'flip_vertical': False,
    'grayscale': False,
    'threshold': False,
    'threshold_value': 128,
    'brightness': 0,
    'contrast': 1.0,
    'gamma': 1.0,
    'saturation': 1.0,
    'blur': False,
    'blur_kernel_size': 5,
    'sharpen': False,
    'sharpen_strength': 1.0,
    'histogram_equalization': False,
    'edge_detection': False,
    'edge_threshold1': 100,
    'edge_threshold2': 200,
}

# Camera parameter defaults
CAMERA_PARAM_DEFAULTS = {
    'width': 1920,
    'height': 1080,
    'exposure_time': 10000,
    'gain': 1.0,
    'acquisition_frame_rate': 30,
    'pixel_format': 'BGRa8',
    'balance_white_auto': 'Off',
}


def add_dll_paths(camera_type: str):
    """
    Add DLL paths to system PATH for specified camera type
    
    Args:
        camera_type: Camera type ('ids', 'mshot', 'hikrobot')
        
    Returns:
        True if paths were added, False otherwise
    """
    if camera_type not in DLL_PATHS:
        logger.warning(f"Unknown camera type: {camera_type}")
        return False
    
    platform = 'windows' if sys.platform == 'win32' else 'linux'
    paths = DLL_PATHS[camera_type].get(platform, [])
    
    added_paths = []
    for path in paths:
        if os.path.exists(path):
            # Add to PATH environment variable
            current_path = os.environ.get('PATH', '')
            if path not in current_path:
                os.environ['PATH'] = path + os.pathsep + current_path
                added_paths.append(path)
                logger.info(f"Added to PATH: {path}")
            
            # Also add to sys.path for Python imports
            if path not in sys.path:
                sys.path.insert(0, path)
                logger.debug(f"Added to sys.path: {path}")
        else:
            logger.debug(f"Path does not exist: {path}")
    
    if added_paths:
        logger.info(f"Added {len(added_paths)} DLL paths for {camera_type}")
        return True
    else:
        logger.warning(f"No valid DLL paths found for {camera_type}")
        return False


def find_dll(camera_type: str, dll_name: str = None) -> str:
    """
    Find DLL file in configured paths
    
    Args:
        camera_type: Camera type ('ids', 'mshot', 'hikrobot')
        dll_name: DLL filename (optional, uses default if not provided)
        
    Returns:
        Full path to DLL if found, empty string otherwise
    """
    if camera_type not in DLL_PATHS:
        return ''
    
    if dll_name is None:
        platform = 'windows' if sys.platform == 'win32' else 'linux'
        dll_files = DLL_PATHS[camera_type].get('dll_files', [])
        # Select appropriate DLL for platform
        if platform == 'windows':
            dll_name = next((f for f in dll_files if f.endswith('.dll')), dll_files[0] if dll_files else '')
        else:
            dll_name = next((f for f in dll_files if f.endswith('.so')), dll_files[0] if dll_files else '')
    
    if not dll_name:
        return ''
    
    platform = 'windows' if sys.platform == 'win32' else 'linux'
    paths = DLL_PATHS[camera_type].get(platform, [])
    
    for path in paths:
        dll_path = os.path.join(path, dll_name)
        if os.path.exists(dll_path):
            logger.info(f"Found DLL: {dll_path}")
            return dll_path
    
    logger.warning(f"DLL not found: {dll_name} for {camera_type}")
    return ''


def check_camera_sdk_availability() -> dict:
    """
    Check which camera SDKs are available
    
    Returns:
        Dictionary with availability status for each camera type
    """
    availability = {
        'ids': False,
        'mshot': False,
        'hikrobot': False
    }
    
    # Check IDS
    try:
        import pyueye
        availability['ids'] = True
        logger.info("IDS uEye SDK is available")
    except ImportError:
        logger.debug("IDS uEye SDK not available")
    
    # Check Mshot
    try:
        import mshot
        availability['mshot'] = True
        logger.info("Mshot SDK is available")
    except ImportError:
        logger.debug("Mshot SDK not available")
    
    # Check Hikrobot
    try:
        from MvCameraControl_class import *
        availability['hikrobot'] = True
        logger.info("Hikrobot MVS SDK is available")
    except ImportError:
        logger.debug("Hikrobot MVS SDK not available")
    
    return availability


def initialize_camera_sdk(camera_type: str) -> bool:
    """
    Initialize camera SDK by adding DLL paths and checking availability
    
    Args:
        camera_type: Camera type ('ids', 'mshot', 'hikrobot')
        
    Returns:
        True if SDK is available, False otherwise
    """
    # Add DLL paths first
    add_dll_paths(camera_type)
    
    # Check availability
    availability = check_camera_sdk_availability()
    return availability.get(camera_type, False)


def get_service_config() -> dict:
    """
    Get camera service configuration
    
    Returns:
        Service configuration dictionary
    """
    return SERVICE_CONFIG.copy()


def get_image_processing_defaults() -> dict:
    """
    Get default image processing parameters
    
    Returns:
        Default parameters dictionary
    """
    return IMAGE_PROCESSING_DEFAULTS.copy()


def get_camera_param_defaults() -> dict:
    """
    Get default camera parameters
    
    Returns:
        Default camera parameters dictionary
    """
    return CAMERA_PARAM_DEFAULTS.copy()


# Initialize DLL paths for Hikrobot on import (since it's already integrated)
if sys.platform == 'win32':
    add_dll_paths('hikrobot')

