# WebSocket Camera Service Documentation

## Overview

The WebSocket Camera Service provides real-time camera communication using WebSocket protocol, supporting IDS, Mshot, and Hikrobot cameras. This service can run alongside or independently of the existing HTTP-based camera server.

## Features

- **Multi-Camera Support**: IDS uEye, Mshot, and Hikrobot cameras
- **WebSocket Communication**: Real-time bidirectional communication
- **Frame Streaming**: Low-latency JPEG frame streaming
- **Parameter Control**: Exposure, gain, resolution, and other camera parameters
- **Device Discovery**: Automatic camera enumeration
- **Compatible with ENVISION**: Uses existing Hikrobot SDK integration

## Installation

### Prerequisites

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Install camera SDKs (optional, based on camera type):
   - **IDS**: Install uEye SDK and `pyueye` package
   - **Mshot**: Install Mshot SDK
   - **Hikrobot**: MVS SDK (already included in ENVISION)

## Usage

### Starting the Service

#### Option 1: WebSocket Service Only
```bash
cd backend
python start_websocket_service.py
```

#### Option 2: Both HTTP and WebSocket Services
```bash
cd backend
python start_all_services.py
```

#### Option 3: HTTP Service Only (Existing)
```bash
cd backend
python start_server.py
```

### WebSocket Endpoint

- **URL**: `ws://localhost:8765`
- **Protocol**: WebSocket (binary frames for JPEG, JSON for commands)

## API Reference

### Commands

All commands are sent as JSON messages:

```json
{
  "command": "command_name",
  "index": 0,
  "camera_type": "hikrobot",
  // ... other parameters
}
```

### Command List

#### 1. Set Camera Type
```json
{
  "command": "set_camera",
  "camera_type": "hikrobot"  // or "ids", "mshot"
}
```

**Response:**
```json
{
  "message": "Camera type set to hikrobot",
  "status": "success"
}
```

#### 2. Get Available Devices
```json
{
  "command": "get_devices"
}
```

**Response:**
```json
{
  "devices": [
    {
      "index": 0,
      "type": "hikrobot",
      "model": "MV-CA050-10GC",
      "serial": "12345678",
      "ip": "192.168.1.100",
      "interface": "GigE"
    }
  ]
}
```

#### 3. Connect to Camera
```json
{
  "command": "connect",
  "index": 0
}
```

**Response:**
```json
{
  "message": "Connected to camera 0",
  "status": "success",
  "width": 2448,
  "height": 2048
}
```

#### 4. Start Stream
```json
{
  "command": "start_stream",
  "index": 0,
  "width": 1920,  // optional
  "height": 1080  // optional
}
```

**Response:**
```json
{
  "message": "Stream started",
  "status": "success",
  "frame_width": 1920,
  "frame_height": 1080
}
```

After this, the server will send JPEG frames as binary messages.

#### 5. Stop Stream
```json
{
  "command": "stop_stream",
  "index": 0
}
```

**Response:**
```json
{
  "message": "Stream stopped",
  "status": "success"
}
```

#### 6. Disconnect Camera
```json
{
  "command": "disconnect",
  "index": 0
}
```

**Response:**
```json
{
  "message": "Disconnected from camera 0",
  "status": "success"
}
```

#### 7. Get Parameter Minimum
```json
{
  "command": "getMin",
  "index": 0,
  "parameter": "ExposureTime"
}
```

**Response:**
```json
{
  "min": {
    "ExposureTime": 10.0
  }
}
```

#### 8. Get Parameter Maximum
```json
{
  "command": "getMax",
  "index": 0,
  "parameter": "ExposureTime"
}
```

**Response:**
```json
{
  "max": {
    "ExposureTime": 100000.0
  }
}
```

#### 9. Get Current Parameters
```json
{
  "command": "getCurrent",
  "index": 0
}
```

**Response:**
```json
{
  "current": {
    "Width": 2448,
    "Height": 2048,
    "ExposureTime": 50000.0,
    "Gain": 10.0,
    "AcquisitionFrameRate": 30.0,
    "PixelFormat": 17301505,
    "BalanceWhiteAuto": "Off"
  }
}
```

#### 10. Set Parameter
```json
{
  "command": "setValue",
  "index": 0,
  "parameter": "ExposureTime",
  "value": 30000
}
```

**Response:**
```json
{
  "command": "setValue",
  "parameter": "ExposureTime",
  "value": 30000,
  "status": "success"
}
```

#### 11. Save Settings
```json
{
  "command": "saveSettings",
  "index": 0
}
```

**Response:**
```json
{
  "message": "Camera settings saved successfully",
  "status": "success"
}
```

## Supported Parameters

### Common Parameters
- `Width` - Image width (pixels)
- `Height` - Image height (pixels)
- `ExposureTime` - Exposure time (microseconds)
- `Gain` - Gain value
- `AcquisitionFrameRate` - Frame rate (fps)

### Hikrobot-Specific
- `PixelFormat` - Pixel format enum
- `BalanceWhiteAuto` - Auto white balance ("Off", "Once", "Continuous")
- `DigitalZoom` - Digital zoom factor

## Frame Streaming

After starting a stream, the server sends JPEG-encoded frames as binary WebSocket messages at approximately 30 FPS.

### Frame Format
- **Type**: Binary (JPEG)
- **Quality**: 90% (configurable in code)
- **Rate**: ~30 FPS (0.033s interval)

## Example Scripts

### Python Examples

See `backend/examples/` directory for complete examples:

1. **`camera_service_example.py`** - Comprehensive example with all features
2. **`quick_start_example.py`** - Simple quick-start example

Run examples:
```bash
cd backend/examples
python camera_service_example.py
```

## Example Client Code

### JavaScript/TypeScript
```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
  // Set camera type
  ws.send(JSON.stringify({
    command: 'set_camera',
    camera_type: 'hikrobot'
  }));
  
  // Get devices
  ws.send(JSON.stringify({
    command: 'get_devices'
  }));
  
  // Connect to first camera
  ws.send(JSON.stringify({
    command: 'connect',
    index: 0
  }));
  
  // Start stream
  ws.send(JSON.stringify({
    command: 'start_stream',
    index: 0,
    width: 1920,
    height: 1080
  }));
};

ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    // Binary frame data (JPEG)
    const imageUrl = URL.createObjectURL(event.data);
    document.getElementById('camera-view').src = imageUrl;
  } else {
    // JSON response
    const data = JSON.parse(event.data);
    console.log('Response:', data);
  }
};
```

### Python
```python
import asyncio
import websockets
import json
import cv2
import numpy as np

async def camera_client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Set camera type
        await websocket.send(json.dumps({
            "command": "set_camera",
            "camera_type": "hikrobot"
        }))
        
        # Get devices
        await websocket.send(json.dumps({
            "command": "get_devices"
        }))
        response = await websocket.recv()
        devices = json.loads(response)
        print(f"Found {len(devices['devices'])} devices")
        
        # Connect to first camera
        await websocket.send(json.dumps({
            "command": "connect",
            "index": 0
        }))
        
        # Start stream
        await websocket.send(json.dumps({
            "command": "start_stream",
            "index": 0
        }))
        
        # Receive frames
        frame_count = 0
        while True:
            message = await websocket.recv()
            if isinstance(message, bytes):
                # JPEG frame
                nparr = np.frombuffer(message, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.imshow('Camera', frame)
                    frame_count += 1
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            else:
                # JSON response
                print("Response:", json.loads(message))

asyncio.run(camera_client())
```

## Integration with ENVISION

The WebSocket service uses the same Hikrobot SDK integration as the existing HTTP server:

- Uses `MvCameraControl_class.py` for Hikrobot cameras
- Compatible with existing camera initialization
- Frame capture method matches `camera_server.py` implementation
- Supports digital zoom and resolution control

## Troubleshooting

### Camera Not Found
- Ensure camera SDK is installed
- Check camera is powered and connected
- Verify camera drivers are installed
- For Hikrobot: Ensure `MvCameraControl.dll` is in PATH

### Connection Issues
- Check WebSocket server is running on port 8765
- Verify firewall allows WebSocket connections
- Check for port conflicts

### Frame Streaming Issues
- Ensure camera is connected before starting stream
- Check camera is not in use by another application
- Verify camera supports requested resolution

## Architecture

```
WebSocket Client
    ↓
WebSocket Server (port 8765)
    ↓
CameraBase (Abstract)
    ├── IDSCamera
    ├── MshotCamera
    └── HikrobotCamera (uses MvCamera)
        ↓
Camera SDK
    ↓
Hardware Camera
```

## Notes

- The service runs independently of the HTTP server
- Multiple clients can connect, but each camera can only be used by one client at a time
- Frame streaming stops automatically when client disconnects
- All cameras are cleaned up on service shutdown

## Future Enhancements

- Multi-client camera sharing
- Image processing pipeline
- Recording functionality
- Event-based notifications
- Authentication/authorization

