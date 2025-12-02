"""
ENVISION - Unified Backend Launcher
Starts all backend services: HTTP Camera Server and WebSocket Camera Service
Run this single file to start everything!
"""

import sys
import os
import asyncio
import threading
import logging
import signal
import time
from pathlib import Path

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        # Python < 3.7 or reconfigure failed
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging with UTF-8 encoding
class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)
        if sys.platform == 'win32':
            try:
                if hasattr(stream, 'reconfigure'):
                    stream.reconfigure(encoding='utf-8')
            except (AttributeError, ValueError):
                pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        UTF8StreamHandler(sys.stdout),
        logging.FileHandler('logs/backend.log', mode='a', encoding='utf-8') if os.path.exists('logs') else UTF8StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_event = threading.Event()

def setup_environment():
    """Initialize DLL paths and check SDK availability"""
    try:
        from camera_config import (
            add_dll_paths,
            check_camera_sdk_availability,
            initialize_camera_sdk,
            get_service_config
        )
        
        logger.info("=" * 60)
        logger.info("ENVISION Backend Services - Initializing")
        logger.info("=" * 60)
        
        # Initialize DLL paths for all camera types
        logger.info("Setting up camera SDK DLL paths...")
        for camera_type in ['ids', 'mshot', 'hikrobot']:
            try:
                add_dll_paths(camera_type)
                if camera_type == 'hikrobot':
                    initialize_camera_sdk(camera_type)
            except Exception as e:
                logger.debug(f"Could not add DLL paths for {camera_type}: {e}")
        
        # Check SDK availability
        availability = check_camera_sdk_availability()
        logger.info("Camera SDK Availability:")
        for cam_type, is_available in availability.items():
            status = "[OK] Available" if is_available else "[X] Not Available"
            logger.info(f"  {cam_type.upper():12} : {status}")
        
        # Get service configuration
        config = get_service_config()
        logger.info(f"\nService Configuration:")
        logger.info(f"  WebSocket Host: {config.get('host', 'localhost')}")
        logger.info(f"  WebSocket Port: {config.get('port', 8765)}")
        logger.info(f"  HTTP Server Port: 5000")
        
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_http_server():
    """Run HTTP Flask camera server in a separate thread"""
    try:
        logger.info("Starting HTTP Camera Server...")
        
        # Import here to avoid conflicts
        from camera_server import app
        from camera_config import add_dll_paths
        
        # Ensure DLL paths are set
        add_dll_paths('hikrobot')
        
        # Run Flask app
        logger.info("HTTP Server running on http://0.0.0.0:5000")
        logger.info("API endpoints available at http://localhost:5000/api/")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Set to False for production
            threaded=True,
            use_reloader=False  # Disable reloader when running in thread
        )
        
    except Exception as e:
        logger.error(f"Error in HTTP server: {e}")
        import traceback
        traceback.print_exc()
        shutdown_event.set()


def run_websocket_service():
    """Run WebSocket camera service using asyncio"""
    try:
        logger.info("Starting WebSocket Camera Service...")
        
        from websocket_camera_service import main
        from camera_config import get_service_config
        
        config = get_service_config()
        host = config.get('host', 'localhost')
        port = config.get('port', 8765)
        
        logger.info(f"WebSocket Server running on ws://{host}:{port}")
        
        # Run asyncio event loop
        asyncio.run(main())
        
    except Exception as e:
        logger.error(f"Error in WebSocket service: {e}")
        import traceback
        traceback.print_exc()
        shutdown_event.set()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("\n" + "=" * 60)
    logger.info("Shutdown signal received. Stopping all services...")
    logger.info("=" * 60)
    shutdown_event.set()
    sys.exit(0)


def main():
    """Main entry point - starts all services"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize environment
    if not setup_environment():
        logger.error("Initialization failed. Exiting.")
        sys.exit(1)
    
    logger.info("\n" + "=" * 60)
    logger.info("Starting ENVISION Backend Services")
    logger.info("=" * 60)
    logger.info("Services:")
    logger.info("  1. HTTP Camera Server    -> http://localhost:5000")
    logger.info("  2. WebSocket Service     -> ws://localhost:8765")
    logger.info("")
    logger.info("Press Ctrl+C to stop all services")
    logger.info("=" * 60)
    logger.info("")
    
    # Start HTTP server in a separate thread
    http_thread = threading.Thread(
        target=run_http_server,
        daemon=True,
        name="HTTP-Server"
    )
    http_thread.start()
    
    # Give HTTP server time to start
    time.sleep(2)
    
    # Check if HTTP server started successfully
    if not http_thread.is_alive():
        logger.error("HTTP server failed to start!")
        sys.exit(1)
    
    logger.info("[OK] HTTP Server started successfully")
    
    # Start WebSocket service in main thread (blocking)
    try:
        logger.info("[OK] Starting WebSocket Service...")
        run_websocket_service()
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("=" * 60)
        logger.info("All services stopped.")
        logger.info("=" * 60)
        shutdown_event.set()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        shutdown_event.set()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

