"""
Example usage of camera service and image processing
Original structure - compatible with both import styles
"""

import asyncio
import websockets
import json
import cv2
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import image processing - try both possible names
try:
    from image_processing_utils import ImageProcessing
except ImportError:
    try:
        from image_processing import ImageProcessing
    except ImportError:
        print("Error: Could not import ImageProcessing")
        sys.exit(1)


async def test_camera_service():
    """Test camera service connection and commands"""
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to camera service")
            
            # Set camera type
            print("\n1. Setting camera type to 'ids'...")
            await websocket.send(json.dumps({
                "command": "set_camera",
                "camera_type": "ids"
            }))
            response = await websocket.recv()
            print(f"Response: {json.loads(response)}")
            
            # Get devices
            print("\n2. Getting available devices...")
            await websocket.send(json.dumps({
                "command": "get_devices"
            }))
            response = await websocket.recv()
            devices = json.loads(response)
            print(f"Found {len(devices.get('devices', []))} devices")
            for device in devices.get('devices', []):
                print(f"  - {device.get('model', 'Unknown')} (Serial: {device.get('serial', 'N/A')})")
            
            # Connect to first device (if available)
            if devices.get('devices'):
                device_index = devices['devices'][0]['index']
                print(f"\n3. Connecting to device {device_index}...")
                await websocket.send(json.dumps({
                    "command": "connect",
                    "index": device_index
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
                
                # Get current parameters
                print("\n4. Getting current camera parameters...")
                await websocket.send(json.dumps({
                    "command": "getCurrent",
                    "index": device_index
                }))
                response = await websocket.recv()
                params = json.loads(response)
                print(f"Parameters: {json.dumps(params.get('current', {}), indent=2)}")
                
                # Set exposure time
                print("\n5. Setting exposure time to 5000...")
                await websocket.send(json.dumps({
                    "command": "setValue",
                    "index": device_index,
                    "parameter": "ExposureTime",
                    "value": 5000
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
                
                # Start stream
                print("\n6. Starting stream...")
                await websocket.send(json.dumps({
                    "command": "start_stream",
                    "index": device_index,
                    "width": 1920,
                    "height": 1080
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
                
                # Receive frames
                print("\n7. Receiving frames (5 frames)...")
                frame_count = 0
                while frame_count < 5:
                    try:
                        frame_data = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        if isinstance(frame_data, bytes):
                            frame_count += 1
                            print(f"  Received frame {frame_count} ({len(frame_data)} bytes)")
                    except asyncio.TimeoutError:
                        print("  Timeout waiting for frame")
                        break
                
                # Stop stream
                print("\n8. Stopping stream...")
                await websocket.send(json.dumps({
                    "command": "stop_stream",
                    "index": device_index
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
                
                # Disconnect
                print("\n9. Disconnecting...")
                await websocket.send(json.dumps({
                    "command": "disconnect",
                    "index": device_index
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
            
    except websockets.exceptions.ConnectionRefused:
        print("Error: Could not connect to camera service.")
        print("Make sure camera_service.py is running on ws://localhost:8765")
        print("Start it with: python start_websocket_service.py")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_image_processing():
    """Test image processing functions"""
    print("\n" + "=" * 60)
    print("Testing Image Processing")
    print("=" * 60)
    
    # Create a test image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (100, 100), (540, 380), (255, 255, 255), -1)
    cv2.circle(test_image, (320, 240), 50, (0, 0, 255), -1)
    
    print("Original image created: 640x480")
    
    # Test rotation
    rotated = ImageProcessing.rotate_image(test_image, 45)
    print(f"✓ Rotation: {rotated.shape}")
    
    # Test flip
    flipped_h = ImageProcessing.flip_horizontal(test_image)
    print(f"✓ Horizontal flip: {flipped_h.shape}")
    
    # Test grayscale
    gray = ImageProcessing.to_grayscale(test_image)
    print(f"✓ Grayscale: {gray.shape}")
    
    # Test threshold
    thresh = ImageProcessing.apply_threshold(test_image, 128)
    print(f"✓ Threshold: {thresh.shape}")
    
    # Test brightness/contrast
    adjusted = ImageProcessing.adjust_brightness_contrast(test_image, brightness=20, contrast=1.2)
    print(f"✓ Brightness/Contrast: {adjusted.shape}")
    
    # Test gamma
    gamma_corrected = ImageProcessing.apply_gamma_correction(test_image, 1.5)
    print(f"✓ Gamma correction: {gamma_corrected.shape}")
    
    # Test blur
    blurred = ImageProcessing.apply_gaussian_blur(test_image, 5)
    print(f"✓ Gaussian blur: {blurred.shape}")
    
    # Test sharpen
    sharpened = ImageProcessing.apply_sharpen(test_image, 1.5)
    print(f"✓ Sharpen: {sharpened.shape}")
    
    # Test all operations
    print("\nTesting combined operations...")
    operations = {
        'rotation': 90,
        'flip_horizontal': True,
        'grayscale': True,
        'threshold': True,
        'threshold_value': 128,
        'brightness': 10,
        'contrast': 1.2,
        'gamma': 1.5,
        'sharpen': True,
        'sharpen_strength': 1.5
    }
    processed = ImageProcessing.apply_all_operations(test_image, operations)
    print(f"✓ Combined operations: {processed.shape}")
    
    print("\nAll image processing tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Weldmet Camera Service - Example Usage")
    print("=" * 60)
    
    # Test image processing (doesn't require camera service)
    test_image_processing()
    
    # Test camera service (requires service to be running)
    print("\n" + "=" * 60)
    print("Testing Camera Service Connection")
    print("=" * 60)
    print("Note: Camera service must be running for this test")
    print("Start it with: python start_websocket_service.py")
    print("=" * 60)
    
    try:
        asyncio.run(test_camera_service())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()

