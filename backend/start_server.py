from camera_server import app
from camera_config import check_camera_sdk_availability, add_dll_paths
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Initialize DLL paths for Hikrobot (already integrated)
    add_dll_paths('hikrobot')
    
    # Check SDK availability
    availability = check_camera_sdk_availability()
    logger.info(f"Camera SDK availability: {availability}")
    
    logger.info("Starting ENVISION Camera Server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 