# ENVISION Examples

Example scripts demonstrating camera service and image processing functionality.

## Files

### `camera_service_example.py`

Comprehensive example demonstrating:
- WebSocket camera service connection
- Camera device discovery
- Camera parameter control
- Frame streaming and processing
- Image processing utilities
- Camera configuration checking

## Usage

### Prerequisites

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start WebSocket camera service (optional, for camera tests):
```bash
cd backend
python start_websocket_service.py
```

### Run Examples

```bash
cd backend/examples
python camera_service_example.py
```

## Example Output

### Image Processing Tests
- Tests all image processing operations
- Creates test images and applies transformations
- Validates operation results

### Camera Configuration Tests
- Checks SDK availability
- Finds DLL files
- Displays configuration settings

### Camera Service Tests (requires running service)
- Connects to WebSocket service
- Discovers cameras
- Connects and controls camera
- Streams and processes frames
- Disconnects cleanly

## Customization

Modify the example script to:
- Test different camera types (ids, mshot, hikrobot)
- Apply custom image processing operations
- Test specific camera parameters
- Process frames in real-time

## Notes

- Image processing tests run independently
- Camera service tests require WebSocket service to be running
- All tests include error handling and informative output

