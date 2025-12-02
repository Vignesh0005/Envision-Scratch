# Camera Configuration and DLL Setup

## Overview

The camera configuration system manages DLL paths, SDK initialization, and service settings for all supported camera types (IDS, Mshot, and Hikrobot).

## Configuration File

**`backend/camera_config.py`** - Central configuration for camera services

### Features

1. **DLL Path Management**: Automatic detection and addition of DLL paths to system PATH
2. **SDK Availability Checking**: Verify which camera SDKs are installed
3. **Service Configuration**: WebSocket and HTTP service settings
4. **Default Parameters**: Image processing and camera parameter defaults

## DLL Paths

### Hikrobot (MVS SDK)
- **Windows**:
  - `C:\Program Files\MVS\Development\Bin\x64`
  - `C:\Program Files (x86)\MVS\Development\Bin\x64`
  - `backend/libs/hikrobot`
  - `backend/MvImport` (ENVISION's existing directory)
  - `backend` (current directory)

- **Linux**:
  - `/usr/lib`
  - `/usr/local/lib`
  - `backend/libs/hikrobot`

- **DLL Files**:
  - Windows: `MvCameraControl.dll`
  - Linux: `libMvCameraControl.so`

### IDS (uEye SDK)
- **Windows**:
  - `C:\Program Files\IDS\uEye\Develop\Bin64`
  - `C:\Program Files (x86)\IDS\uEye\Develop\Bin64`
  - `backend/libs/ids`

- **Linux**:
  - `/usr/lib`
  - `/usr/local/lib`
  - `backend/libs/ids`

- **DLL Files**:
  - Windows: `ueye_api.dll`
  - Linux: `libueye_api.so`

### Mshot
- **Windows**:
  - `C:\Program Files\Mshot`
  - `C:\Program Files (x86)\Mshot`
  - `backend/libs/mshot`

- **Linux**:
  - `/usr/lib`
  - `/usr/local/lib`
  - `backend/libs/mshot`

- **DLL Files**:
  - Windows: `mshot.dll`
  - Linux: `libmshot.so`

## Usage

### Check SDK Availability

```python
from camera_config import check_camera_sdk_availability

availability = check_camera_sdk_availability()
# Returns: {'ids': False, 'mshot': False, 'hikrobot': True}
```

### Add DLL Paths

```python
from camera_config import add_dll_paths

# Add Hikrobot DLL paths
add_dll_paths('hikrobot')

# Add IDS DLL paths
add_dll_paths('ids')
```

### Find DLL File

```python
from camera_config import find_dll

# Find Hikrobot DLL
dll_path = find_dll('hikrobot', 'MvCameraControl.dll')
if dll_path:
    print(f"Found DLL at: {dll_path}")
```

### Initialize Camera SDK

```python
from camera_config import initialize_camera_sdk

# Initialize and check availability
if initialize_camera_sdk('hikrobot'):
    print("Hikrobot SDK is ready")
else:
    print("Hikrobot SDK not available")
```

### Get Configuration

```python
from camera_config import (
    get_service_config,
    get_image_processing_defaults,
    get_camera_param_defaults
)

# Service configuration
service_config = get_service_config()
# Returns: {'host': 'localhost', 'port': 8765, ...}

# Image processing defaults
img_defaults = get_image_processing_defaults()

# Camera parameter defaults
camera_defaults = get_camera_param_defaults()
```

## Utility Script

**`backend/check_camera_sdks.py`** - Command-line tool to check SDK availability

### Usage

```bash
cd backend
python check_camera_sdks.py
```

### Output

```
============================================================
ENVISION Camera SDK Checker
============================================================

Checking Camera SDK Availability...
------------------------------------------------------------
IDS          : ✗ Not Available
MSHOT        : ✗ Not Available
HIKROBOT     : ✓ Available

Checking DLL Files...
------------------------------------------------------------

HIKROBOT:
  ✓ Found: C:\Program Files\MVS\Development\Bin\x64\MvCameraControl.dll

Service Configuration...
------------------------------------------------------------
host                  : localhost
port                  : 8765
max_connections       : 10
frame_rate            : 30
jpeg_quality          : 90
buffer_size           : 1048576
============================================================
Check complete!
============================================================
```

## Integration

### HTTP Camera Server

The HTTP server (`camera_server.py`) automatically:
- Adds Hikrobot DLL paths on import
- Initializes DLL paths when starting Hikrobot camera
- Checks SDK availability on startup

### WebSocket Camera Service

The WebSocket service (`websocket_camera_service.py`):
- Adds DLL paths when setting camera type
- Checks SDK availability on startup
- Provides SDK status in responses
- Uses service configuration for host/port

### Startup Scripts

Both `start_server.py` and `start_websocket_service.py`:
- Initialize DLL paths on startup
- Display SDK availability status
- Use configuration for service settings

## Configuration Options

### Service Configuration

```python
SERVICE_CONFIG = {
    'host': 'localhost',        # Service host
    'port': 8765,               # WebSocket port
    'max_connections': 10,      # Max concurrent connections
    'frame_rate': 30,           # Target frame rate
    'jpeg_quality': 90,         # JPEG compression quality
    'buffer_size': 1024 * 1024, # Buffer size (1MB)
}
```

### Image Processing Defaults

All default values for image processing operations (brightness, contrast, gamma, etc.)

### Camera Parameter Defaults

Default camera settings (width, height, exposure, gain, etc.)

## Custom DLL Paths

To add custom DLL paths, edit `camera_config.py`:

```python
DLL_PATHS['hikrobot']['windows'].append(r'C:\Custom\Path\To\DLLs')
```

Or place DLLs in:
- `backend/libs/hikrobot/`
- `backend/libs/ids/`
- `backend/libs/mshot/`

## Troubleshooting

### DLL Not Found

1. Check if SDK is installed
2. Verify DLL paths in configuration
3. Run `check_camera_sdks.py` to diagnose
4. Ensure DLL architecture matches Python (64-bit vs 32-bit)

### SDK Import Errors

1. Verify Python packages are installed:
   - IDS: `pip install pyueye` (if available)
   - Mshot: Install Mshot SDK package
   - Hikrobot: Already integrated via `MvCameraControl_class.py`

2. Check DLL paths are added:
   ```python
   from camera_config import add_dll_paths
   add_dll_paths('hikrobot')
   ```

3. Verify DLL is accessible:
   ```python
   from camera_config import find_dll
   dll_path = find_dll('hikrobot')
   print(dll_path)
   ```

### Path Issues

- On Windows, ensure paths use backslashes or raw strings
- Check file permissions for DLL directories
- Verify DLL architecture matches system

## Platform Support

- **Windows**: Full support for all camera types
- **Linux**: Supported (paths configured, may need SDK installation)

## Notes

- Hikrobot SDK is automatically initialized on import (Windows)
- DLL paths are added to both `PATH` environment variable and `sys.path`
- Configuration is read-only (use functions to access, not direct modification)
- All paths are checked for existence before adding

