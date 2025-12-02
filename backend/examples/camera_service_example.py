"""
Example usage of camera service and image processing
Demonstrates WebSocket camera service and image processing utilities
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

from image_processing_utils import ImageProcessing
# Alias for compatibility
try:
    from image_processing_utils import ImageProcessing as ImageProcessingUtils
except ImportError:
    pass


async def test_camera_service():
    """Test camera service connection and commands"""
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to camera service")
            
            # Set camera type
            print("\n1. Setting camera type to 'hikrobot'...")
            await websocket.send(json.dumps({
                "command": "set_camera",
                "camera_type": "hikrobot"
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
                print(f"  - {device.get('model', 'Unknown')} (Serial: {device.get('serial', 'N/A')}, Type: {device.get('type', 'N/A')})")
            
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
                
                # Get parameter min/max
                print("\n5. Getting exposure time range...")
                await websocket.send(json.dumps({
                    "command": "getMin",
                    "index": device_index,
                    "parameter": "ExposureTime"
                }))
                response = await websocket.recv()
                min_params = json.loads(response)
                print(f"Min: {min_params.get('min', {})}")
                
                await websocket.send(json.dumps({
                    "command": "getMax",
                    "index": device_index,
                    "parameter": "ExposureTime"
                }))
                response = await websocket.recv()
                max_params = json.loads(response)
                print(f"Max: {max_params.get('max', {})}")
                
                # Set exposure time
                print("\n6. Setting exposure time to 50000...")
                await websocket.send(json.dumps({
                    "command": "setValue",
                    "index": device_index,
                    "parameter": "ExposureTime",
                    "value": 50000
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
                
                # Start stream
                print("\n7. Starting stream...")
                await websocket.send(json.dumps({
                    "command": "start_stream",
                    "index": device_index,
                    "width": 1920,
                    "height": 1080
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
                
                # Receive frames
                print("\n8. Receiving frames (5 frames)...")
                frame_count = 0
                frames_received = []
                
                while frame_count < 5:
                    try:
                        frame_data = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        if isinstance(frame_data, bytes):
                            frame_count += 1
                            print(f"  Received frame {frame_count} ({len(frame_data)} bytes)")
                            
                            # Decode and process frame
                            nparr = np.frombuffer(frame_data, np.uint8)
                            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            if frame is not None:
                                frames_received.append(frame)
                                print(f"    Decoded frame: {frame.shape}")
                    except asyncio.TimeoutError:
                        print("  Timeout waiting for frame")
                        break
                
                # Process received frames with image processing
                if frames_received:
                    print("\n9. Processing frames with image processing utilities...")
                    test_frame = frames_received[0]
                    
                    # Apply various processing operations
                    processed_frames = {
                        'original': test_frame,
                        'grayscale': ImageProcessing.to_grayscale(test_frame),
                        'brightness_contrast': ImageProcessing.adjust_brightness_contrast(test_frame, brightness=20, contrast=1.2),
                        'gamma': ImageProcessing.apply_gamma_correction(test_frame, 1.5),
                        'blur': ImageProcessing.apply_gaussian_blur(test_frame, 5),
                        'sharpen': ImageProcessing.apply_sharpen(test_frame, 1.5)
                    }
                    
                    for name, processed in processed_frames.items():
                        print(f"  ✓ {name}: {processed.shape}")
                
                # Stop stream
                print("\n10. Stopping stream...")
                await websocket.send(json.dumps({
                    "command": "stop_stream",
                    "index": device_index
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
                
                # Disconnect
                print("\n11. Disconnecting...")
                await websocket.send(json.dumps({
                    "command": "disconnect",
                    "index": device_index
                }))
                response = await websocket.recv()
                print(f"Response: {json.loads(response)}")
            else:
                print("\nNo devices found. Skipping connection test.")
            
    except websockets.exceptions.ConnectionRefused:
        print("Error: Could not connect to camera service.")
        print("Make sure WebSocket camera service is running:")
        print("  cd backend")
        print("  python start_websocket_service.py")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_image_processing():
    """Test image processing functions"""
    print("\n" + "=" * 60)
    print("Testing Image Processing Utilities")
    print("=" * 60)
    
    # Create a test image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (100, 100), (540, 380), (255, 255, 255), -1)
    cv2.circle(test_image, (320, 240), 50, (0, 0, 255), -1)
    cv2.putText(test_image, "ENVISION Test", (200, 400), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    print("Original image created: 640x480")
    
    # Test rotation
    rotated = ImageProcessing.rotate_image(test_image, 45)
    print(f"✓ Rotation (45°): {rotated.shape}")
    
    # Test 90-degree rotation
    rotated_90 = ImageProcessing.rotate_image_90(test_image, 'clockwise')
    print(f"✓ Rotation (90° clockwise): {rotated_90.shape}")
    
    # Test flip
    flipped_h = ImageProcessing.flip_horizontal(test_image)
    print(f"✓ Horizontal flip: {flipped_h.shape}")
    
    flipped_v = ImageProcessing.flip_vertical(test_image)
    print(f"✓ Vertical flip: {flipped_v.shape}")
    
    flipped_both = ImageProcessing.flip_both(test_image)
    print(f"✓ Both flips: {flipped_both.shape}")
    
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
    
    # Test saturation
    saturated = ImageProcessing.adjust_saturation(test_image, 1.3)
    print(f"✓ Saturation adjustment: {saturated.shape}")
    
    # Test blur
    blurred = ImageProcessing.apply_gaussian_blur(test_image, 5)
    print(f"✓ Gaussian blur: {blurred.shape}")
    
    # Test sharpen
    sharpened = ImageProcessing.apply_sharpen(test_image, 1.5)
    print(f"✓ Sharpen: {sharpened.shape}")
    
    # Test histogram equalization
    equalized = ImageProcessing.apply_histogram_equalization(test_image)
    print(f"✓ Histogram equalization: {equalized.shape}")
    
    # Test edge detection
    edges = ImageProcessing.apply_canny_edge_detection(test_image, 100, 200)
    print(f"✓ Canny edge detection: {edges.shape}")
    
    # Test resize
    resized = ImageProcessing.resize_image(test_image, width=320, height=240)
    print(f"✓ Resize: {resized.shape}")
    
    resized_scale = ImageProcessing.resize_image(test_image, scale=0.5)
    print(f"✓ Resize (scale 0.5): {resized_scale.shape}")
    
    # Test invert
    inverted = ImageProcessing.invert_image(test_image)
    print(f"✓ Invert: {inverted.shape}")
    
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
        'saturation': 1.15,
        'sharpen': True,
        'sharpen_strength': 1.5,
        'histogram_equalization': True
    }
    processed = ImageProcessing.apply_all_operations(test_image, operations)
    print(f"✓ Combined operations: {processed.shape}")
    
    print("\nAll image processing tests passed!")


def test_camera_config():
    """Test camera configuration utilities"""
    print("\n" + "=" * 60)
    print("Testing Camera Configuration")
    print("=" * 60)
    
    try:
        from camera_config import (
            check_camera_sdk_availability,
            find_dll,
            get_service_config,
            get_image_processing_defaults,
            get_camera_param_defaults
        )
        
        # Check SDK availability
        print("\n1. Checking camera SDK availability...")
        availability = check_camera_sdk_availability()
        for camera_type, is_available in availability.items():
            status = "✓ Available" if is_available else "✗ Not Available"
            print(f"  {camera_type.upper():12} : {status}")
        
        # Find DLLs
        print("\n2. Finding DLL files...")
        for camera_type in ['ids', 'mshot', 'hikrobot']:
            dll_path = find_dll(camera_type)
            if dll_path:
                print(f"  {camera_type.upper():12} : ✓ {dll_path}")
            else:
                print(f"  {camera_type.upper():12} : ✗ Not found")
        
        # Get configurations
        print("\n3. Service configuration...")
        service_config = get_service_config()
        for key, value in service_config.items():
            print(f"  {key:20} : {value}")
        
        print("\n4. Image processing defaults...")
        img_defaults = get_image_processing_defaults()
        print(f"  Total defaults: {len(img_defaults)} parameters")
        
        print("\n5. Camera parameter defaults...")
        camera_defaults = get_camera_param_defaults()
        for key, value in camera_defaults.items():
            print(f"  {key:20} : {value}")
        
        print("\nCamera configuration tests passed!")
        
    except ImportError as e:
        print(f"Error importing camera_config: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("ENVISION Camera Service - Example Usage")
    print("=" * 60)
    
    # Test image processing (doesn't require camera service)
    test_image_processing()
    
    # Test camera configuration
    test_camera_config()
    
    # Test camera service (requires service to be running)
    print("\n" + "=" * 60)
    print("Testing Camera Service Connection")
    print("=" * 60)
    print("Note: WebSocket camera service must be running for this test")
    print("Start it with:")
    print("  cd backend")
    print("  python start_websocket_service.py")
    print("=" * 60)
    
    try:
        asyncio.run(test_camera_service())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Example usage complete!")
    print("=" * 60)

