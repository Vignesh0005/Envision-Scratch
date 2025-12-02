# ENVISION Installation Guide

Complete installation guide for ENVISION microscopy image analysis platform, including camera SDKs and dependencies.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Python Dependencies](#python-dependencies)
3. [Camera SDK Installation](#camera-sdk-installation)
4. [Project Setup](#project-setup)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11 or Linux
- **Python**: 3.8 or higher
- **Node.js**: 18+ and npm 9+ (for frontend)
- **Git**: For cloning the repository

### Required Software

- Python 3.8+
- pip (Python package manager)
- Node.js and npm
- PostgreSQL 12+ (optional, for production database)

---

## Python Dependencies

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask and Flask-CORS
- OpenCV (opencv-python)
- NumPy, SciPy
- scikit-image, scikit-learn
- Pillow
- WebSockets
- And other required packages

### 3. Verify Installation

```bash
python -c "import cv2, numpy, flask; print('Core dependencies installed successfully')"
```

---

## Camera SDK Installation

### Hikrobot MVS SDK (Recommended - Already Integrated)

**Status**: Already integrated in ENVISION via `MvCameraControl_class.py`

#### Installation Steps:

1. **Download MVS SDK**
   - Visit: [Hikrobot MVS SDK Download](https://www.hikrobotics.com/en/machinevision/service/download)
   - Download the latest MVS SDK for your platform (Windows/Linux)

2. **Install SDK**
   - Run the installer
   - Default installation paths:
     - Windows: `C:\Program Files\MVS\Development\Bin\x64`
     - Linux: `/usr/lib` or `/usr/local/lib`

3. **Verify DLL Location**
   - Windows: Ensure `MvCameraControl.dll` is in the SDK bin directory
   - Linux: Ensure `libMvCameraControl.so` is in library path

4. **ENVISION Integration**
   - ENVISION already includes `MvCameraControl_class.py`
   - DLL paths are automatically configured via `camera_config.py`
   - No additional Python package installation needed

#### Verification:

```bash
cd backend
python check_camera_sdks.py
```

Should show:
```
HIKROBOT     : ✓ Available
```

---

### IDS uEye SDK (Optional)

**Required for**: IDS camera support via WebSocket service

#### Installation Steps:

1. **Download uEye SDK**
   - Visit: [IDS Imaging uEye SDK](https://en.ids-imaging.com/downloads.html)
   - **What to select on the website:**
     - **Product Family**: `uEye` or `All`
     - **Model**: `All Models` or your specific camera model
     - **Interface**: 
       - `USB 3.0` for USB cameras (most common)
       - `GigE` or `Ethernet` for network cameras
       - `USB 2.0 / USB 3.0` if you have both types
     - **OS**: `Windows 10/11 64-bit`
     - **SDK**: `uEye SDK` (latest version)
   - Register/login may be required
   - See `IDS_SDK_DOWNLOAD_GUIDE.md` for detailed selection guide

2. **Install SDK**
   - Run the installer
   - Default installation paths:
     - Windows: `C:\Program Files\IDS\uEye\Develop\Bin64`
     - Linux: `/usr/lib` or `/usr/local/lib`

3. **Install Python Package**
   ```bash
   pip install pyueye
   ```
   Note: `pyueye` is the Python wrapper. You still need the SDK DLL files.

4. **Verify Installation**
   ```bash
   cd backend
   python check_ids_sdk.py
   ```

5. **Configure DLL Paths**
   - DLL paths are automatically configured in `camera_config.py`
   - Or manually add to `backend/libs/ids/`

#### Verification:

```bash
cd backend
python check_camera_sdks.py
```

Should show:
```
IDS          : ✓ Available
```

---

### Mshot SDK (Optional)

**Required for**: Mshot camera support via WebSocket service

#### Installation Steps:

1. **Contact Vendor**
   - Contact Mshot vendor for SDK download
   - Request SDK for your platform (Windows/Linux)

2. **Install SDK**
   - Follow vendor's installation instructions
   - Default installation paths:
     - Windows: `C:\Program Files\Mshot`
     - Linux: `/usr/lib` or `/usr/local/lib`

3. **Install Python Package** (if available)
   ```bash
   pip install mshot
   ```
   Note: Package may not be available via pip. Use vendor-provided Python bindings.

4. **Configure DLL Paths**
   - DLL paths are automatically configured in `camera_config.py`
   - Or manually add to `backend/libs/mshot/`

#### Verification:

```bash
cd backend
python check_camera_sdks.py
```

Should show:
```
MSHOT        : ✓ Available
```

---

## Project Setup

### 1. Clone Repository (if not already done)

```bash
git clone https://github.com/Vignesh0005/Envision-Scratch.git
cd Envision-Scratch
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Verify camera SDKs
python check_camera_sdks.py

# Test server startup
python start_server.py
```

### 3. Frontend Setup

```bash
# From project root
npm install

# Start development server
npm start
```

### 4. Electron Setup (Optional)

```bash
# Install Electron dependencies
npm install

# Run in development mode
npm run electron-dev
```

---

## Verification

### 1. Check Camera SDKs

```bash
cd backend
python check_camera_sdks.py
```

Expected output:
```
============================================================
ENVISION Camera SDK Checker
============================================================

Checking Camera SDK Availability...
------------------------------------------------------------
IDS          : ✗ Not Available (or ✓ Available)
MSHOT        : ✗ Not Available (or ✓ Available)
HIKROBOT     : ✓ Available

Checking DLL Files...
------------------------------------------------------------
HIKROBOT:
  ✓ Found: C:\Program Files\MVS\Development\Bin\x64\MvCameraControl.dll
```

### 2. Test HTTP Camera Server

```bash
cd backend
python start_server.py
```

Should start on `http://localhost:5000`

### 3. Test WebSocket Camera Service

```bash
cd backend
python start_websocket_service.py
```

Should start on `ws://localhost:8765`

### 4. Run Example Scripts

```bash
cd backend/examples
python camera_service_example.py
```

### 5. Test Image Processing

```bash
cd backend/examples
python quick_start_example.py
```

---

## Quick Installation Summary

### Minimal Setup (Hikrobot Only)

```bash
# 1. Install Python dependencies
cd backend
pip install -r requirements.txt

# 2. Download and install Hikrobot MVS SDK
# (Follow Hikrobot SDK installation steps above)

# 3. Verify
python check_camera_sdks.py

# 4. Start server
python start_server.py
```

### Full Setup (All Camera Types)

```bash
# 1. Install Python dependencies
cd backend
pip install -r requirements.txt

# 2. Install camera SDKs
# - Hikrobot MVS SDK (required)
# - IDS uEye SDK (optional)
# - Mshot SDK (optional)

# 3. Verify all SDKs
python check_camera_sdks.py

# 4. Start services
python start_all_services.py
```

---

## Troubleshooting

### Python Dependencies Issues

**Problem**: `pip install` fails

**Solutions**:
- Update pip: `python -m pip install --upgrade pip`
- Use virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  venv\Scripts\activate     # Windows
  pip install -r requirements.txt
  ```

### Camera SDK Not Found

**Problem**: `check_camera_sdks.py` shows SDK as not available

**Solutions**:
1. Verify SDK is installed
2. Check DLL paths in `camera_config.py`
3. Manually add DLL to `backend/libs/{camera_type}/`
4. Add DLL directory to system PATH
5. Restart Python/application

### DLL Loading Errors

**Problem**: `ImportError` or DLL not found errors

**Solutions**:
1. Ensure DLL architecture matches Python (64-bit vs 32-bit)
2. Check DLL is in configured paths
3. Verify file permissions
4. On Windows: Check if Visual C++ Redistributables are installed
5. Run as administrator if needed

### WebSocket Connection Refused

**Problem**: Cannot connect to WebSocket service

**Solutions**:
1. Verify service is running: `python start_websocket_service.py`
2. Check port 8765 is not in use
3. Verify firewall settings
4. Check service logs in `backend/logs/`

### Import Errors

**Problem**: `ModuleNotFoundError` for camera modules

**Solutions**:
1. Ensure you're in the correct directory
2. Check `sys.path` includes backend directory
3. Verify all dependencies are installed
4. Use absolute imports or add to PYTHONPATH

---

## Platform-Specific Notes

### Windows

- DLLs are typically `.dll` files
- Install SDKs to Program Files directories
- May require administrator privileges
- Visual C++ Redistributables may be needed

### Linux

- Libraries are typically `.so` files
- May need to set `LD_LIBRARY_PATH`:
  ```bash
  export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
  ```
- May require `sudo` for system-wide installation
- Check library dependencies: `ldd libMvCameraControl.so`

---

## Next Steps After Installation

1. **Configure Calibration**
   - Set up camera calibration for measurements
   - See calibration documentation

2. **Test Camera Connection**
   - Run example scripts
   - Verify frame capture works

3. **Explore Features**
   - Try image processing operations
   - Test analysis modules
   - Experiment with measurement tools

4. **Production Setup**
   - Configure database (if using PostgreSQL)
   - Set up logging
   - Configure service ports
   - Set up auto-start scripts

---

## Support

For issues or questions:
- Check logs in `backend/logs/`
- Run diagnostic: `python check_camera_sdks.py`
- Review documentation in project root
- Check camera SDK vendor documentation

---

## Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Hikrobot MVS SDK installed
- [ ] (Optional) IDS uEye SDK installed
- [ ] (Optional) Mshot SDK installed
- [ ] Camera SDKs verified (`check_camera_sdks.py`)
- [ ] HTTP server starts successfully
- [ ] WebSocket service starts successfully
- [ ] Example scripts run without errors
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Application runs in development mode

---

**Installation Complete!** You're ready to use ENVISION for microscopy image analysis.

