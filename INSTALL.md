# ENVISION Installation Guide

**For the most comprehensive installation instructions, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**

**For quick setup, see [QUICK_START.md](QUICK_START.md)**

## Quick Installation Steps

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Camera SDKs

#### Hikrobot MVS SDK (Required for Camera Features)
1. Download from [Hikrobot MVS SDK](https://www.hikrobotics.com/en/machinevision/service/download)
2. Install to default location
3. Verify: `python check_camera_sdks.py`

#### IDS uEye SDK (Optional)
1. Download from [IDS Imaging](https://en.ids-imaging.com/downloads.html)
2. Install SDK and Python bindings

#### Mshot SDK (Optional)
1. Contact vendor for SDK
2. Install according to vendor instructions

### 3. Verify Installation

```bash
cd backend
python check_camera_sdks.py
```

### 4. Start Services

```bash
# HTTP Camera Server
cd backend
python start_server.py

# OR WebSocket Camera Service
python start_websocket_service.py

# OR Both Services
python start_all_services.py
```

## Full Installation Guide

See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for:
- Detailed step-by-step instructions
- Platform-specific installation (Windows/Linux)
- Troubleshooting guide
- Configuration options
- Database setup
- Frontend setup

## Quick Start

See [QUICK_START.md](QUICK_START.md) for a 5-minute setup guide.
