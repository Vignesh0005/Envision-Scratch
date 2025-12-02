"""
Quick Start Example - Simple camera and image processing usage
"""

import asyncio
import websockets
import json
import cv2
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_processing_utils import ImageProcessing


async def simple_camera_test():
    """Simple camera connection test"""
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as ws:
            # Set camera type
            await ws.send(json.dumps({
                "command": "set_camera",
                "camera_type": "hikrobot"
            }))
            print("✓ Camera type set")
            
            # Get devices
            await ws.send(json.dumps({"command": "get_devices"}))
            devices = json.loads(await ws.recv())
            print(f"✓ Found {len(devices.get('devices', []))} devices")
            
            if devices.get('devices'):
                idx = devices['devices'][0]['index']
                
                # Connect
                await ws.send(json.dumps({"command": "connect", "index": idx}))
                print("✓ Connected to camera")
                
                # Start stream
                await ws.send(json.dumps({
                    "command": "start_stream",
                    "index": idx
                }))
                print("✓ Stream started")
                
                # Get one frame
                frame_data = await asyncio.wait_for(ws.recv(), timeout=3.0)
                if isinstance(frame_data, bytes):
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        print(f"✓ Received frame: {frame.shape}")
                        
                        # Process frame
                        processed = ImageProcessing.to_grayscale(frame)
                        print(f"✓ Processed frame: {processed.shape}")
                
                # Cleanup
                await ws.send(json.dumps({"command": "stop_stream", "index": idx}))
                await ws.send(json.dumps({"command": "disconnect", "index": idx}))
                print("✓ Disconnected")
                
    except websockets.exceptions.ConnectionRefused:
        print("✗ Camera service not running. Start it with:")
        print("  python start_websocket_service.py")
    except Exception as e:
        print(f"✗ Error: {e}")


def simple_image_processing_test():
    """Simple image processing test"""
    # Create test image
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (350, 250), (255, 255, 255), -1)
    
    # Apply operations
    gray = ImageProcessing.to_grayscale(img)
    bright = ImageProcessing.adjust_brightness_contrast(img, brightness=30, contrast=1.3)
    rotated = ImageProcessing.rotate_image(img, 45)
    
    print("✓ Image processing test complete")
    print(f"  Original: {img.shape}")
    print(f"  Grayscale: {gray.shape}")
    print(f"  Brightness adjusted: {bright.shape}")
    print(f"  Rotated: {rotated.shape}")


if __name__ == "__main__":
    print("=" * 50)
    print("ENVISION Quick Start Example")
    print("=" * 50)
    
    print("\n1. Image Processing Test:")
    simple_image_processing_test()
    
    print("\n2. Camera Service Test:")
    print("   (Requires WebSocket service to be running)")
    asyncio.run(simple_camera_test())
    
    print("\n" + "=" * 50)
    print("Quick start complete!")
    print("=" * 50)

