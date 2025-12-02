# ENVISION Backend - Quick Start

## Single File to Run Everything

**Just run this one file to start all backend services:**

```bash
cd backend
python run_all.py
```

That's it! This single command starts:
- ✅ HTTP Camera Server (port 5000)
- ✅ WebSocket Camera Service (port 8765)
- ✅ All camera SDK initialization
- ✅ DLL path management

## What Gets Started

### 1. HTTP Camera Server
- **URL**: `http://localhost:5000`
- **API**: `http://localhost:5000/api/`
- Provides REST API for camera control and image processing

### 2. WebSocket Camera Service
- **URL**: `ws://localhost:8765`
- Provides real-time camera streaming and control

## Features

- ✅ Automatic DLL path setup
- ✅ SDK availability checking
- ✅ Graceful shutdown (Ctrl+C)
- ✅ Logging to console and file
- ✅ Error handling and recovery

## Alternative: Individual Services

If you only need one service:

```bash
# HTTP Server only
python start_server.py

# WebSocket Service only
python start_websocket_service.py

# Both (alternative method)
python start_all_services.py
```

## Troubleshooting

**Port already in use?**
- Change ports in `camera_config.py` or stop conflicting services

**DLL not found?**
- Run `python check_camera_sdks.py` to diagnose
- Run `python find_mvs_dll.py` to locate DLLs

**Services not starting?**
- Check logs in `logs/backend.log`
- Verify Python dependencies: `pip install -r requirements.txt`

