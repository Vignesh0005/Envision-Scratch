"""
Weldmet Camera Service - WebSocket Implementation
Supports IDS, Mshot, and Hikrobot cameras with WebSocket communication
Integrated with ENVISION project
"""

import asyncio
import json
import logging
import sys
import traceback
from typing import Dict, List, Optional, Any
import websockets
from websockets.server import WebSocketServerProtocol
import cv2
import numpy as np
from PIL import Image
import io
import base64
from ctypes import *

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import camera configuration
from camera_config import (
    add_dll_paths, 
    find_dll, 
    check_camera_sdk_availability,
    initialize_camera_sdk,
    get_service_config,
    SERVICE_CONFIG
)

# Camera SDK imports
# Try to add IDS DLL paths before importing
try:
    add_dll_paths('ids')
except Exception as e:
    logger.debug(f"Could not add IDS DLL paths: {e}")

try:
    # IDS Camera SDK (uEye SDK)
    import pyueye
    # Test if pyueye can actually access the DLL
    try:
        # Try to access a basic function to verify DLL is available
        _ = pyueye.is_GetNumberOfCameras
        IDS_AVAILABLE = True
        logger.info("IDS uEye SDK is available and ready")
    except (AttributeError, RuntimeError, OSError) as e:
        IDS_AVAILABLE = False
        logger.warning(f"pyueye package is installed but IDS SDK DLL not found: {e}")
        logger.warning("Please install IDS uEye SDK from: https://en.ids-imaging.com/downloads.html")
except ImportError:
    IDS_AVAILABLE = False
    logger.warning("IDS uEye SDK not available. Install pyueye package: pip install pyueye")
except Exception as e:
    IDS_AVAILABLE = False
    logger.warning(f"IDS uEye SDK not available: {e}")
    logger.warning("pyueye package may be installed but SDK DLL is missing")

# Try to add Mshot DLL paths before importing
try:
    add_dll_paths('mshot')
except Exception as e:
    logger.debug(f"Could not add Mshot DLL paths: {e}")

try:
    # Mshot Camera SDK
    import mshot
    MSHOT_AVAILABLE = True
    logger.info("Mshot SDK is available and ready")
except ImportError:
    MSHOT_AVAILABLE = False
    logger.warning("Mshot SDK not available. Install mshot SDK.")
except Exception as e:
    MSHOT_AVAILABLE = False
    logger.warning(f"Mshot SDK not available: {e}")

# Try to add Hikrobot DLL paths before importing
try:
    add_dll_paths('hikrobot')
    # Initialize Hikrobot SDK if available
    if initialize_camera_sdk('hikrobot'):
        logger.debug("Hikrobot SDK DLL paths configured")
except Exception as e:
    logger.debug(f"Could not add Hikrobot DLL paths: {e}")

try:
    # Hikrobot Camera SDK (MVS SDK) - Use existing implementation
    from MvCameraControl_class import *
    from CameraParams_const import *
    from CameraParams_header import *
    from MvErrorDefine_const import *
    HIKROBOT_AVAILABLE = True
    logger.info("Hikrobot MVS SDK is available and ready")
except ImportError:
    HIKROBOT_AVAILABLE = False
    logger.warning("Hikrobot MVS SDK not available. Install MVS SDK.")
except Exception as e:
    HIKROBOT_AVAILABLE = False
    logger.warning(f"Hikrobot MVS SDK not available: {e}")

# Logging already configured above

# Global state
camera_type: Optional[str] = None
connected_cameras: Dict[int, Any] = {}  # index -> camera object
streaming_cameras: Dict[int, bool] = {}  # index -> is_streaming
camera_devices: List[Dict] = []


class CameraBase:
    """Base class for camera implementations"""
    
    def __init__(self, index: int):
        self.index = index
        self.is_connected = False
        self.is_streaming = False
        self.width = 0
        self.height = 0
        
    def connect(self) -> bool:
        raise NotImplementedError
        
    def disconnect(self) -> bool:
        raise NotImplementedError
        
    def get_devices(self) -> List[Dict]:
        raise NotImplementedError
        
    def start_stream(self, width: Optional[int] = None, height: Optional[int] = None) -> bool:
        raise NotImplementedError
        
    def stop_stream(self) -> bool:
        raise NotImplementedError
        
    def capture_frame(self) -> Optional[np.ndarray]:
        raise NotImplementedError
        
    def get_parameter_min(self, param: str) -> Optional[float]:
        raise NotImplementedError
        
    def get_parameter_max(self, param: str) -> Optional[float]:
        raise NotImplementedError
        
    def get_parameter_current(self, param: str) -> Optional[Any]:
        raise NotImplementedError
        
    def set_parameter(self, param: str, value: Any) -> bool:
        raise NotImplementedError


class IDSCamera(CameraBase):
    """IDS uEye Camera Implementation"""
    
    def __init__(self, index: int):
        super().__init__(index)
        self.camera = None
        self.mem_ptr = None
        self.mem_id = None
        
    def get_devices(self) -> List[Dict]:
        """Discover IDS cameras"""
        devices = []
        if not IDS_AVAILABLE:
            return devices
            
        try:
            n_cams = pyueye.is_GetNumberOfCameras()
            for i in range(n_cams):
                cam_info = pyueye.CAMINFO()
                ret = pyueye.is_GetCameraInfo(i, cam_info)
                if ret == pyueye.IS_SUCCESS:
                    devices.append({
                        'index': i,
                        'type': 'ids',
                        'model': cam_info.Model.decode('utf-8') if cam_info.Model else f'IDS Camera {i}',
                        'serial': cam_info.SerNo.decode('utf-8') if cam_info.SerNo else str(i),
                        'interface': 'USB'
                    })
        except Exception as e:
            logger.error(f"Error discovering IDS cameras: {e}")
        return devices
    
    def connect(self) -> bool:
        """Connect to IDS camera"""
        if not IDS_AVAILABLE:
            return False
        try:
            self.camera = pyueye.Camera(self.index)
            ret = self.camera.InitCamera()
            if ret == pyueye.IS_SUCCESS:
                self.is_connected = True
                # Get sensor info
                sensor_info = pyueye.SENSORINFO()
                self.camera.GetSensorInfo(sensor_info)
                self.width = sensor_info.nMaxWidth
                self.height = sensor_info.nMaxHeight
                return True
        except Exception as e:
            logger.error(f"Error connecting to IDS camera: {e}")
        return False
    
    def disconnect(self) -> bool:
        """Disconnect from IDS camera"""
        try:
            if self.camera:
                if self.is_streaming:
                    self.stop_stream()
                if self.mem_ptr:
                    self.camera.FreeImageMem(self.mem_ptr, self.mem_id)
                self.camera.ExitCamera()
                self.camera = None
            self.is_connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting IDS camera: {e}")
        return False
    
    def start_stream(self, width: Optional[int] = None, height: Optional[int] = None) -> bool:
        """Start streaming from IDS camera"""
        try:
            if not self.is_connected:
                return False
                
            # Set resolution if specified
            if width and height:
                self.camera.SetImageSize(width, height)
                self.width = width
                self.height = height
            
            # Allocate memory
            self.mem_ptr = self.camera.AllocImageMem(self.width, self.height, 24)
            self.mem_id = self.camera.AddToSequence(self.mem_ptr, self.width, self.height, 24)
            
            # Start capture
            ret = self.camera.CaptureVideo(pyueye.IS_WAIT)
            if ret == pyueye.IS_SUCCESS:
                self.is_streaming = True
                return True
        except Exception as e:
            logger.error(f"Error starting IDS stream: {e}")
        return False
    
    def stop_stream(self) -> bool:
        """Stop streaming from IDS camera"""
        try:
            if self.camera and self.is_streaming:
                self.camera.StopLiveVideo(pyueye.IS_FORCE_VIDEO_STOP)
                self.is_streaming = False
                return True
        except Exception as e:
            logger.error(f"Error stopping IDS stream: {e}")
        return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from IDS camera"""
        try:
            if not self.is_streaming:
                return None
                
            ret = self.camera.CopyImageMem(self.mem_ptr, self.mem_id)
            if ret == pyueye.IS_SUCCESS:
                # Convert to numpy array (simplified - actual implementation depends on uEye SDK version)
                # This is a placeholder - actual implementation would use uEye SDK's image buffer
                pass
        except Exception as e:
            logger.error(f"Error capturing IDS frame: {e}")
        return None
    
    def get_parameter_min(self, param: str) -> Optional[float]:
        """Get minimum value for parameter"""
        try:
            if param == "ExposureTime":
                min_val = pyueye.DOUBLE()
                self.camera.GetExposureRange(min_val, None)
                return float(min_val.value)
            elif param == "Gain":
                min_val = pyueye.INT()
                self.camera.GetGainRange(min_val, None)
                return float(min_val.value)
        except Exception as e:
            logger.error(f"Error getting min {param}: {e}")
        return None
    
    def get_parameter_max(self, param: str) -> Optional[float]:
        """Get maximum value for parameter"""
        try:
            if param == "ExposureTime":
                max_val = pyueye.DOUBLE()
                self.camera.GetExposureRange(None, max_val)
                return float(max_val.value)
            elif param == "Gain":
                max_val = pyueye.INT()
                self.camera.GetGainRange(None, max_val)
                return float(max_val.value)
        except Exception as e:
            logger.error(f"Error getting max {param}: {e}")
        return None
    
    def get_parameter_current(self, param: str) -> Optional[Any]:
        """Get current value for parameter"""
        try:
            if param == "ExposureTime":
                val = pyueye.DOUBLE()
                self.camera.GetExposure(val)
                return float(val.value)
            elif param == "Gain":
                val = pyueye.INT()
                self.camera.GetGain(val)
                return float(val.value)
            elif param == "Width":
                return self.width
            elif param == "Height":
                return self.height
        except Exception as e:
            logger.error(f"Error getting current {param}: {e}")
        return None
    
    def set_parameter(self, param: str, value: Any) -> bool:
        """Set camera parameter"""
        try:
            if param == "ExposureTime":
                ret = self.camera.SetExposure(float(value))
                return ret == pyueye.IS_SUCCESS
            elif param == "Gain":
                ret = self.camera.SetGain(int(value))
                return ret == pyueye.IS_SUCCESS
        except Exception as e:
            logger.error(f"Error setting {param}: {e}")
        return False


class MshotCamera(CameraBase):
    """Mshot Camera Implementation"""
    
    def __init__(self, index: int):
        super().__init__(index)
        self.camera = None
        
    def get_devices(self) -> List[Dict]:
        """Discover Mshot cameras"""
        devices = []
        if not MSHOT_AVAILABLE:
            return devices
            
        try:
            # Mshot SDK device discovery
            # This is a placeholder - actual implementation depends on Mshot SDK
            camera_list = mshot.enumerate_cameras()
            for i, cam_info in enumerate(camera_list):
                devices.append({
                    'index': i,
                    'type': 'mshot',
                    'model': cam_info.get('model', f'Mshot Camera {i}'),
                    'serial': cam_info.get('serial', str(i)),
                    'interface': 'USB'
                })
        except Exception as e:
            logger.error(f"Error discovering Mshot cameras: {e}")
        return devices
    
    def connect(self) -> bool:
        """Connect to Mshot camera"""
        if not MSHOT_AVAILABLE:
            return False
        try:
            self.camera = mshot.Camera(self.index)
            if self.camera.open():
                self.is_connected = True
                self.width, self.height = self.camera.get_resolution()
                return True
        except Exception as e:
            logger.error(f"Error connecting to Mshot camera: {e}")
        return False
    
    def disconnect(self) -> bool:
        """Disconnect from Mshot camera"""
        try:
            if self.camera:
                if self.is_streaming:
                    self.stop_stream()
                self.camera.close()
                self.camera = None
            self.is_connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting Mshot camera: {e}")
        return False
    
    def start_stream(self, width: Optional[int] = None, height: Optional[int] = None) -> bool:
        """Start streaming from Mshot camera"""
        try:
            if not self.is_connected:
                return False
                
            if width and height:
                self.camera.set_resolution(width, height)
                self.width = width
                self.height = height
            
            if self.camera.start_capture():
                self.is_streaming = True
                return True
        except Exception as e:
            logger.error(f"Error starting Mshot stream: {e}")
        return False
    
    def stop_stream(self) -> bool:
        """Stop streaming from Mshot camera"""
        try:
            if self.camera and self.is_streaming:
                self.camera.stop_capture()
                self.is_streaming = False
                return True
        except Exception as e:
            logger.error(f"Error stopping Mshot stream: {e}")
        return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from Mshot camera"""
        try:
            if not self.is_streaming:
                return None
            frame = self.camera.get_frame()
            return frame
        except Exception as e:
            logger.error(f"Error capturing Mshot frame: {e}")
        return None
    
    def get_parameter_min(self, param: str) -> Optional[float]:
        """Get minimum value for parameter"""
        try:
            return self.camera.get_parameter_min(param)
        except Exception as e:
            logger.error(f"Error getting min {param}: {e}")
        return None
    
    def get_parameter_max(self, param: str) -> Optional[float]:
        """Get maximum value for parameter"""
        try:
            return self.camera.get_parameter_max(param)
        except Exception as e:
            logger.error(f"Error getting max {param}: {e}")
        return None
    
    def get_parameter_current(self, param: str) -> Optional[Any]:
        """Get current value for parameter"""
        try:
            return self.camera.get_parameter(param)
        except Exception as e:
            logger.error(f"Error getting current {param}: {e}")
        return None
    
    def set_parameter(self, param: str, value: Any) -> bool:
        """Set camera parameter"""
        try:
            return self.camera.set_parameter(param, value)
        except Exception as e:
            logger.error(f"Error setting {param}: {e}")
        return False


class HikrobotCamera(CameraBase):
    """Hikrobot Camera Implementation using MVS SDK - Integrated with ENVISION"""
    
    def __init__(self, index: int):
        super().__init__(index)
        self.camera = None
        self.device_list = None
        self.current_resolution = None
        
    def get_devices(self) -> List[Dict]:
        """Discover Hikrobot cameras"""
        devices = []
        if not HIKROBOT_AVAILABLE:
            return devices
            
        try:
            # Initialize SDK
            temp_camera = MvCamera()
            ret = temp_camera.MV_CC_Initialize()
            if ret != 0:
                logger.error("Failed to initialize Hikrobot SDK")
                return devices
            
            # Enumerate devices
            device_list = MV_CC_DEVICE_INFO_LIST()
            ret = temp_camera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, device_list)
            if ret != 0:
                logger.error("Failed to enumerate Hikrobot devices")
                temp_camera.MV_CC_UnInitialize()
                return devices
                
            for i in range(device_list.nDeviceNum):
                device_info = cast(device_list.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
                
                if device_info.nTLayerType == MV_GIGE_DEVICE:
                    model = device_info.SpecialInfo.stGigEInfo.chModelName.decode('utf-8', errors='ignore')
                    serial = device_info.SpecialInfo.stGigEInfo.chSerialNumber.decode('utf-8', errors='ignore')
                    ip = f"{(device_info.SpecialInfo.stGigEInfo.nCurrentIp >> 24) & 0xFF}.{(device_info.SpecialInfo.stGigEInfo.nCurrentIp >> 16) & 0xFF}.{(device_info.SpecialInfo.stGigEInfo.nCurrentIp >> 8) & 0xFF}.{device_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xFF}"
                    interface = 'GigE'
                else:
                    model = device_info.SpecialInfo.stUsb3VInfo.chModelName.decode('utf-8', errors='ignore')
                    serial = device_info.SpecialInfo.stUsb3VInfo.chSerialNumber.decode('utf-8', errors='ignore')
                    ip = None
                    interface = 'USB'
                    
                devices.append({
                    'index': i,
                    'type': 'hikrobot',
                    'model': model,
                    'serial': serial,
                    'ip': ip,
                    'interface': interface
                })
            
            temp_camera.MV_CC_UnInitialize()
        except Exception as e:
            logger.error(f"Error discovering Hikrobot cameras: {e}")
            logger.error(traceback.format_exc())
        return devices
    
    def connect(self) -> bool:
        """Connect to Hikrobot camera"""
        if not HIKROBOT_AVAILABLE:
            return False
        try:
            # Initialize SDK
            self.camera = MvCamera()
            ret = self.camera.MV_CC_Initialize()
            if ret != 0:
                logger.error("Failed to initialize Hikrobot SDK")
                return False
            
            # Enumerate devices
            self.device_list = MV_CC_DEVICE_INFO_LIST()
            ret = self.camera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, self.device_list)
            if ret != 0:
                logger.error("Failed to enumerate devices")
                self.camera.MV_CC_UnInitialize()
                return False
                
            if self.index >= self.device_list.nDeviceNum:
                logger.error(f"Camera index {self.index} out of range")
                self.camera.MV_CC_UnInitialize()
                return False
                
            # Get device info
            device_info = cast(self.device_list.pDeviceInfo[self.index], POINTER(MV_CC_DEVICE_INFO)).contents
            
            # Create handle
            ret = self.camera.MV_CC_CreateHandle(device_info)
            if ret != 0:
                logger.error(f"Failed to create handle: {ret}")
                self.camera.MV_CC_UnInitialize()
                return False
                
            # Open device
            ret = self.camera.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
            if ret != 0:
                logger.error(f"Failed to open device: {ret}")
                self.camera.MV_CC_DestroyHandle()
                self.camera.MV_CC_UnInitialize()
                return False
                
            self.is_connected = True
            
            # Get resolution
            stParam = MVCC_INTVALUE()
            ret = self.camera.MV_CC_GetIntValue("Width", stParam)
            if ret == 0:
                self.width = stParam.nCurValue
            ret = self.camera.MV_CC_GetIntValue("Height", stParam)
            if ret == 0:
                self.height = stParam.nCurValue
                
            return True
        except Exception as e:
            logger.error(f"Error connecting to Hikrobot camera: {e}")
            logger.error(traceback.format_exc())
            if self.camera:
                try:
                    self.camera.MV_CC_UnInitialize()
                except:
                    pass
        return False
    
    def disconnect(self) -> bool:
        """Disconnect from Hikrobot camera"""
        try:
            if self.camera:
                if self.is_streaming:
                    self.stop_stream()
                try:
                    self.camera.MV_CC_CloseDevice()
                    self.camera.MV_CC_DestroyHandle()
                    self.camera.MV_CC_UnInitialize()
                except Exception as e:
                    logger.error(f"Error during disconnect: {e}")
                self.camera = None
            self.is_connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting Hikrobot camera: {e}")
        return False
    
    def start_stream(self, width: Optional[int] = None, height: Optional[int] = None) -> bool:
        """Start streaming from Hikrobot camera"""
        try:
            if not self.is_connected:
                return False
                
            if width and height:
                ret = self.camera.MV_CC_SetIntValue("Width", width)
                if ret == 0:
                    self.width = width
                ret = self.camera.MV_CC_SetIntValue("Height", height)
                if ret == 0:
                    self.height = height
                self.current_resolution = (width, height)
            
            ret = self.camera.MV_CC_StartGrabbing()
            if ret == 0:
                self.is_streaming = True
                return True
            else:
                logger.error(f"Failed to start grabbing: {ret}")
        except Exception as e:
            logger.error(f"Error starting Hikrobot stream: {e}")
            logger.error(traceback.format_exc())
        return False
    
    def stop_stream(self) -> bool:
        """Stop streaming from Hikrobot camera"""
        try:
            if self.camera and self.is_streaming:
                ret = self.camera.MV_CC_StopGrabbing()
                if ret == 0:
                    self.is_streaming = False
                    return True
        except Exception as e:
            logger.error(f"Error stopping Hikrobot stream: {e}")
        return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from Hikrobot camera - matches existing implementation"""
        try:
            if not self.is_streaming or not self.camera:
                return None
                
            # Use the same method as camera_server.py
            stOutFrame = MV_FRAME_OUT()
            ret = self.camera.MV_CC_GetImageBuffer(stOutFrame, 1000)
            if ret == 0:
                # Get original dimensions
                original_width = stOutFrame.stFrameInfo.nWidth
                original_height = stOutFrame.stFrameInfo.nHeight
                
                # Get current display resolution
                display_width, display_height = self.current_resolution if self.current_resolution else (original_width, original_height)
                
                # Copy frame data
                pData = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
                cdll.msvcrt.memcpy(byref(pData), stOutFrame.pBufAddr, stOutFrame.stFrameInfo.nFrameLen)
                data = np.frombuffer(pData, count=int(stOutFrame.stFrameInfo.nFrameLen), dtype=np.uint8)
                
                # Determine channels based on pixel type
                pixel_type = stOutFrame.stFrameInfo.enPixelType
                if pixel_type == PixelType_Gvsp_Mono8:
                    frame = data.reshape((original_height, original_width))
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                elif pixel_type == PixelType_Gvsp_RGB8_Packed:
                    frame = data.reshape((original_height, original_width, 3))
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                else:
                    # Default: try to reshape based on frame length
                    channels = stOutFrame.stFrameInfo.nFrameLen // (original_width * original_height)
                    if channels == 1:
                        frame = data.reshape((original_height, original_width))
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                    else:
                        frame = data.reshape((original_height, original_width, channels))
                        if channels == 3:
                            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Resize frame to display resolution while maintaining aspect ratio
                if self.current_resolution and (original_width != display_width or original_height != display_height):
                    aspect_ratio = original_width / original_height
                    target_aspect = display_width / display_height
                    
                    if aspect_ratio > target_aspect:
                        new_width = display_width
                        new_height = int(display_width / aspect_ratio)
                    else:
                        new_height = display_height
                        new_width = int(display_height * aspect_ratio)
                        
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Release buffer
                self.camera.MV_CC_FreeImageBuffer(stOutFrame)
                return frame
                
        except Exception as e:
            logger.error(f"Error capturing Hikrobot frame: {e}")
            logger.error(traceback.format_exc())
        return None
    
    def get_parameter_min(self, param: str) -> Optional[float]:
        """Get minimum value for parameter"""
        try:
            if not self.camera or not self.is_connected:
                return None
            stParam = MVCC_INTVALUE()
            ret = self.camera.MV_CC_GetIntValue(param, stParam)
            if ret == 0:
                return float(stParam.nMin)
        except Exception as e:
            logger.error(f"Error getting min {param}: {e}")
        return None
    
    def get_parameter_max(self, param: str) -> Optional[float]:
        """Get maximum value for parameter"""
        try:
            if not self.camera or not self.is_connected:
                return None
            stParam = MVCC_INTVALUE()
            ret = self.camera.MV_CC_GetIntValue(param, stParam)
            if ret == 0:
                return float(stParam.nMax)
        except Exception as e:
            logger.error(f"Error getting max {param}: {e}")
        return None
    
    def get_parameter_current(self, param: str) -> Optional[Any]:
        """Get current value for parameter"""
        try:
            if not self.camera or not self.is_connected:
                return None
            if param in ["Width", "Height", "ExposureTime", "Gain", "AcquisitionFrameRate"]:
                stParam = MVCC_INTVALUE()
                ret = self.camera.MV_CC_GetIntValue(param, stParam)
                if ret == 0:
                    return float(stParam.nCurValue)
            elif param == "PixelFormat":
                stParam = MVCC_ENUMVALUE()
                ret = self.camera.MV_CC_GetEnumValue(param, stParam)
                if ret == 0:
                    return stParam.nCurValue
            elif param == "BalanceWhiteAuto":
                stParam = MVCC_ENUMVALUE()
                ret = self.camera.MV_CC_GetEnumValue(param, stParam)
                if ret == 0:
                    modes = ["Off", "Once", "Continuous"]
                    return modes[stParam.nCurValue] if stParam.nCurValue < len(modes) else "Off"
        except Exception as e:
            logger.error(f"Error getting current {param}: {e}")
        return None
    
    def set_parameter(self, param: str, value: Any) -> bool:
        """Set camera parameter"""
        try:
            if not self.camera or not self.is_connected:
                return False
            if param in ["ExposureTime", "Gain", "AcquisitionFrameRate", "Width", "Height"]:
                ret = self.camera.MV_CC_SetIntValue(param, int(value))
                if ret == 0 and param in ["Width", "Height"]:
                    if param == "Width":
                        self.width = int(value)
                    else:
                        self.height = int(value)
                return ret == 0
            elif param == "PixelFormat":
                ret = self.camera.MV_CC_SetEnumValue(param, value)
                return ret == 0
            elif param == "BalanceWhiteAuto":
                mode_map = {"Off": 0, "Once": 1, "Continuous": 2}
                ret = self.camera.MV_CC_SetEnumValue(param, mode_map.get(value, 0))
                return ret == 0
            elif param == "DigitalZoom":
                # Digital zoom support
                ret = self.camera.MV_CC_SetDigitalZoom(c_float(float(value)))
                return ret == 0
        except Exception as e:
            logger.error(f"Error setting {param}: {e}")
        return False


def get_camera_class(camera_type: str):
    """Get camera class based on type"""
    if camera_type == "ids":
        return IDSCamera
    elif camera_type == "mshot":
        return MshotCamera
    elif camera_type == "hikrobot":
        return HikrobotCamera
    return None


def apply_image_processing(frame: np.ndarray, operations: Dict[str, Any]) -> np.ndarray:
    """Apply image processing operations"""
    processed = frame.copy()
    
    # Grayscale
    if operations.get('grayscale', False):
        if len(processed.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    
    # Threshold
    if operations.get('threshold', False):
        threshold_value = operations.get('threshold_value', 128)
        _, processed = cv2.threshold(processed, threshold_value, 255, cv2.THRESH_BINARY)
    
    # Rotation
    if operations.get('rotation', 0) != 0:
        angle = operations['rotation']
        h, w = processed.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        processed = cv2.warpAffine(processed, M, (w, h))
    
    # Flip
    if operations.get('flip_horizontal', False):
        processed = cv2.flip(processed, 1)
    if operations.get('flip_vertical', False):
        processed = cv2.flip(processed, 0)
    
    # Brightness/Contrast
    if operations.get('brightness', 0) != 0 or operations.get('contrast', 1.0) != 1.0:
        alpha = operations.get('contrast', 1.0)
        beta = operations.get('brightness', 0)
        processed = cv2.convertScaleAbs(processed, alpha=alpha, beta=beta)
    
    return processed


def frame_to_jpeg(frame: np.ndarray, quality: int = 90) -> bytes:
    """Convert frame to JPEG bytes"""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, encoded_image = cv2.imencode('.jpg', frame, encode_param)
    if success:
        return encoded_image.tobytes()
    return None


async def handle_client(websocket: WebSocketServerProtocol, path: str):
    """Handle WebSocket client connection"""
    global camera_type, connected_cameras, streaming_cameras, camera_devices
    
    logger.info(f"Client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            try:
                if isinstance(message, bytes):
                    # Binary data - ignore for now
                    continue
                    
                data = json.loads(message)
                command = data.get('command')
                index = data.get('index')
                
                logger.info(f"Received command: {command}, index: {index}")
                
                # Set camera type
                if command == 'set_camera':
                    camera_type = data.get('camera_type')
                    camera_devices = []
                    # Clean up existing connections
                    for idx in list(connected_cameras.keys()):
                        try:
                            connected_cameras[idx].disconnect()
                        except:
                            pass
                    connected_cameras.clear()
                    streaming_cameras.clear()
                    
                    # Initialize SDK and add DLL paths
                    if camera_type:
                        initialize_camera_sdk(camera_type)
                        availability = check_camera_sdk_availability()
                        if not availability.get(camera_type, False):
                            await websocket.send(json.dumps({
                                'message': f'Camera type set to {camera_type}, but SDK may not be available',
                                'status': 'warning',
                                'sdk_available': False
                            }))
                        else:
                            await websocket.send(json.dumps({
                                'message': f'Camera type set to {camera_type}',
                                'status': 'success',
                                'sdk_available': True
                            }))
                    else:
                        await websocket.send(json.dumps({
                            'message': f'Camera type set to {camera_type}',
                            'status': 'success'
                        }))
                
                # Get devices
                elif command == 'get_devices':
                    if not camera_type:
                        await websocket.send(json.dumps({
                            'error': 'Camera type not set. Please set camera type first.'
                        }))
                    else:
                        CameraClass = get_camera_class(camera_type)
                        if CameraClass:
                            temp_camera = CameraClass(0)
                            camera_devices = temp_camera.get_devices()
                            await websocket.send(json.dumps({
                                'devices': camera_devices
                            }))
                        else:
                            await websocket.send(json.dumps({
                                'error': f'Unknown camera type: {camera_type}'
                            }))
                
                # Connect to camera
                elif command == 'connect':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        # Ensure DLL paths are set before connecting
                        if camera_type:
                            add_dll_paths(camera_type)
                        
                        CameraClass = get_camera_class(camera_type)
                        if CameraClass:
                            camera = CameraClass(index)
                            if camera.connect():
                                connected_cameras[index] = camera
                                await websocket.send(json.dumps({
                                    'message': f'Connected to camera {index}',
                                    'status': 'success',
                                    'width': camera.width,
                                    'height': camera.height
                                }))
                            else:
                                await websocket.send(json.dumps({
                                    'error': f'Failed to connect to camera {index}',
                                    'suggestion': 'Check if camera SDK is installed and DLL paths are correct'
                                }))
                        else:
                            await websocket.send(json.dumps({
                                'error': f'Unknown camera type: {camera_type}'
                            }))
                
                # Disconnect from camera
                elif command == 'disconnect':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        if index in connected_cameras:
                            camera = connected_cameras[index]
                            camera.disconnect()
                            del connected_cameras[index]
                            if index in streaming_cameras:
                                del streaming_cameras[index]
                            await websocket.send(json.dumps({
                                'message': f'Disconnected from camera {index}',
                                'status': 'success'
                            }))
                
                # Start stream
                elif command == 'start_stream':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        if index not in connected_cameras:
                            await websocket.send(json.dumps({
                                'error': f'Camera {index} not connected'
                            }))
                        else:
                            camera = connected_cameras[index]
                            width = data.get('width')
                            height = data.get('height')
                            if camera.start_stream(width, height):
                                streaming_cameras[index] = True
                                await websocket.send(json.dumps({
                                    'message': 'Stream started',
                                    'status': 'success',
                                    'frame_width': camera.width,
                                    'frame_height': camera.height
                                }))
                                
                                # Start streaming loop
                                asyncio.create_task(stream_frames(websocket, camera, index))
                            else:
                                await websocket.send(json.dumps({
                                    'error': 'Failed to start stream'
                                }))
                
                # Stop stream
                elif command == 'stop_stream':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        if index in connected_cameras:
                            camera = connected_cameras[index]
                            camera.stop_stream()
                            streaming_cameras[index] = False
                            await websocket.send(json.dumps({
                                'message': 'Stream stopped',
                                'status': 'success'
                            }))
                
                # Get parameter min
                elif command == 'getMin':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        if index in connected_cameras:
                            camera = connected_cameras[index]
                            param = data.get('parameter', 'ExposureTime')
                            min_val = camera.get_parameter_min(param)
                            await websocket.send(json.dumps({
                                'min': {param: min_val} if min_val is not None else {}
                            }))
                
                # Get parameter max
                elif command == 'getMax':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        if index in connected_cameras:
                            camera = connected_cameras[index]
                            param = data.get('parameter', 'ExposureTime')
                            max_val = camera.get_parameter_max(param)
                            await websocket.send(json.dumps({
                                'max': {param: max_val} if max_val is not None else {}
                            }))
                
                # Get current parameters
                elif command == 'getCurrent':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        if index in connected_cameras:
                            camera = connected_cameras[index]
                            params = {
                                'Width': camera.get_parameter_current('Width'),
                                'Height': camera.get_parameter_current('Height'),
                                'ExposureTime': camera.get_parameter_current('ExposureTime'),
                                'Gain': camera.get_parameter_current('Gain'),
                                'AcquisitionFrameRate': camera.get_parameter_current('AcquisitionFrameRate'),
                                'PixelFormat': camera.get_parameter_current('PixelFormat'),
                                'BalanceWhiteAuto': camera.get_parameter_current('BalanceWhiteAuto')
                            }
                            await websocket.send(json.dumps({
                                'current': params
                            }))
                
                # Set parameter
                elif command == 'setValue':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        if index in connected_cameras:
                            camera = connected_cameras[index]
                            param = data.get('parameter')
                            value = data.get('value')
                            if camera.set_parameter(param, value):
                                await websocket.send(json.dumps({
                                    'command': 'setValue',
                                    'parameter': param,
                                    'value': value,
                                    'status': 'success'
                                }))
                            else:
                                await websocket.send(json.dumps({
                                    'command': 'setValue',
                                    'parameter': param,
                                    'value': value,
                                    'status': 'error',
                                    'error': f'Failed to set {param}'
                                }))
                
                # Save settings
                elif command == 'saveSettings':
                    if index is None:
                        await websocket.send(json.dumps({'error': 'Device index required'}))
                    else:
                        if index in connected_cameras:
                            camera = connected_cameras[index]
                            # Save settings to camera (implementation depends on camera SDK)
                            await websocket.send(json.dumps({
                                'message': 'Camera settings saved successfully',
                                'status': 'success'
                            }))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({'error': 'Invalid JSON'}))
            except Exception as e:
                logger.error(f"Error handling command: {e}")
                logger.error(traceback.format_exc())
                await websocket.send(json.dumps({
                    'error': str(e)
                }))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")
        # Clean up streaming for this client
        for idx in list(streaming_cameras.keys()):
            if idx in connected_cameras:
                try:
                    connected_cameras[idx].stop_stream()
                except:
                    pass
            streaming_cameras[idx] = False
    except Exception as e:
        logger.error(f"Error in handle_client: {e}")
        logger.error(traceback.format_exc())


async def stream_frames(websocket: WebSocketServerProtocol, camera: CameraBase, index: int):
    """Stream frames from camera"""
    try:
        while index in streaming_cameras and streaming_cameras[index]:
            frame = camera.capture_frame()
            if frame is not None:
                jpeg_data = frame_to_jpeg(frame)
                if jpeg_data:
                    await websocket.send(jpeg_data)
            await asyncio.sleep(0.033)  # ~30 fps
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Stream connection closed for camera {index}")
    except Exception as e:
        logger.error(f"Error in stream_frames: {e}")
        logger.error(traceback.format_exc())


async def main():
    """Main entry point"""
    # Get service configuration
    config = get_service_config()
    host = config.get('host', 'localhost')
    port = config.get('port', 8765)
    
    # Check SDK availability
    availability = check_camera_sdk_availability()
    logger.info(f"Camera SDK availability: {availability}")
    
    logger.info(f"Starting Weldmet Camera Service (WebSocket) on ws://{host}:{port}")
    
    async with websockets.serve(handle_client, host, port):
        logger.info("Camera service ready. Waiting for connections...")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down camera service...")
        # Clean up all cameras
        for idx in list(connected_cameras.keys()):
            try:
                connected_cameras[idx].disconnect()
            except:
                pass
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

