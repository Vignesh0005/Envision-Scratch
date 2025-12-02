"""
Start WebSocket Camera Service
Can run alongside or instead of HTTP camera server
"""

import sys
import os
import asyncio
import logging
from websocket_camera_service import main
from camera_config import check_camera_sdk_availability, add_dll_paths, get_service_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Initialize DLL paths
        for camera_type in ['ids', 'mshot', 'hikrobot']:
            add_dll_paths(camera_type)
        
        # Check SDK availability
        availability = check_camera_sdk_availability()
        logger.info(f"Camera SDK availability: {availability}")
        
        config = get_service_config()
        host = config.get('host', 'localhost')
        port = config.get('port', 8765)
        
        print("=" * 60)
        print("Starting WebSocket Camera Service...")
        print(f"WebSocket server will be available at: ws://{host}:{port}")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down WebSocket Camera Service...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting WebSocket service: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

