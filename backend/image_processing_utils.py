"""
Image Processing Utilities for ENVISION
Includes rotation, flip, grayscale, threshold, brightness, contrast, and more
Integrated with existing ENVISION image processing system
"""

import cv2
import numpy as np
from typing import Optional, Tuple, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ImageRotation(Enum):
    """Rotation angles"""
    NONE = 0
    CLOCKWISE_90 = 90
    CLOCKWISE_180 = 180
    CLOCKWISE_270 = 270
    ANTICLOCKWISE_90 = -90
    ANTICLOCKWISE_180 = -180
    ANTICLOCKWISE_270 = -270


class ImageProcessing:
    """Image processing operations - Enhanced utilities for ENVISION"""
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by specified angle
        
        Args:
            image: Input image (numpy array)
            angle: Rotation angle in degrees (positive = clockwise)
            
        Returns:
            Rotated image
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new dimensions
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        # Adjust rotation matrix for new dimensions
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        
        rotated = cv2.warpAffine(image, M, (new_w, new_h), 
                                flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_CONSTANT,
                                borderValue=0)
        return rotated
    
    @staticmethod
    def rotate_image_90(image: np.ndarray, direction: str = 'clockwise') -> np.ndarray:
        """
        Rotate image by 90 degrees (optimized for common case)
        
        Args:
            image: Input image
            direction: 'clockwise' or 'counterclockwise'
            
        Returns:
            Rotated image
        """
        if direction == 'clockwise':
            return np.rot90(image, k=-1)
        else:
            return np.rot90(image, k=1)
    
    @staticmethod
    def flip_horizontal(image: np.ndarray) -> np.ndarray:
        """Flip image horizontally"""
        return cv2.flip(image, 1)
    
    @staticmethod
    def flip_vertical(image: np.ndarray) -> np.ndarray:
        """Flip image vertically"""
        return cv2.flip(image, 0)
    
    @staticmethod
    def flip_both(image: np.ndarray) -> np.ndarray:
        """Flip image both horizontally and vertically"""
        return cv2.flip(image, -1)
    
    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            image: Input image (BGR or RGB)
            
        Returns:
            Grayscale image (still 3-channel for compatibility)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Convert back to 3-channel for consistency
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return image
    
    @staticmethod
    def apply_threshold(image: np.ndarray, threshold_value: int = 128, 
                       threshold_type: int = cv2.THRESH_BINARY) -> np.ndarray:
        """
        Apply threshold to image
        
        Args:
            image: Input image
            threshold_value: Threshold value (0-255)
            threshold_type: OpenCV threshold type
            
        Returns:
            Thresholded image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        _, thresh = cv2.threshold(gray, threshold_value, 255, threshold_type)
        
        # Convert back to 3-channel if original was 3-channel
        if len(image.shape) == 3:
            return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        return thresh
    
    @staticmethod
    def adjust_brightness_contrast(image: np.ndarray, brightness: int = 0, 
                                  contrast: float = 1.0) -> np.ndarray:
        """
        Adjust brightness and contrast
        
        Args:
            image: Input image
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast multiplier (0.0 to 3.0)
            
        Returns:
            Adjusted image
        """
        # Convert to float for calculations
        img_float = image.astype(np.float32)
        
        # Apply contrast
        img_float = img_float * contrast
        
        # Apply brightness
        img_float = img_float + brightness
        
        # Clip values to valid range
        img_float = np.clip(img_float, 0, 255)
        
        return img_float.astype(np.uint8)
    
    @staticmethod
    def apply_gamma_correction(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        """
        Apply gamma correction
        
        Args:
            image: Input image
            gamma: Gamma value (0.1 to 3.0)
            
        Returns:
            Gamma-corrected image
        """
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 
                         for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)
    
    @staticmethod
    def adjust_saturation(image: np.ndarray, saturation: float = 1.0) -> np.ndarray:
        """
        Adjust saturation
        
        Args:
            image: Input image (BGR)
            saturation: Saturation multiplier (0.0 to 2.0)
            
        Returns:
            Saturation-adjusted image
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = hsv[:, :, 1] * saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    @staticmethod
    def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply Gaussian blur
        
        Args:
            image: Input image
            kernel_size: Kernel size (must be odd)
            
        Returns:
            Blurred image
        """
        if kernel_size % 2 == 0:
            kernel_size += 1
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    @staticmethod
    def apply_sharpen(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """
        Apply sharpening filter
        
        Args:
            image: Input image
            strength: Sharpening strength (0.0 to 2.0)
            
        Returns:
            Sharpened image
        """
        kernel = np.array([[-1, -1, -1],
                          [-1, 9 * strength, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)
    
    @staticmethod
    def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
        """
        Apply histogram equalization
        
        Args:
            image: Input image
            
        Returns:
            Equalized image
        """
        if len(image.shape) == 3:
            # Convert to YUV and equalize Y channel
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            return cv2.equalizeHist(image)
    
    @staticmethod
    def apply_canny_edge_detection(image: np.ndarray, 
                                  threshold1: int = 100,
                                  threshold2: int = 200) -> np.ndarray:
        """
        Apply Canny edge detection
        
        Args:
            image: Input image
            threshold1: First threshold
            threshold2: Second threshold
            
        Returns:
            Edge-detected image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        edges = cv2.Canny(gray, threshold1, threshold2)
        
        # Convert back to 3-channel if original was 3-channel
        if len(image.shape) == 3:
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return edges
    
    @staticmethod
    def resize_image(image: np.ndarray, width: Optional[int] = None, 
                    height: Optional[int] = None,
                    scale: Optional[float] = None,
                    interpolation: int = cv2.INTER_LINEAR) -> np.ndarray:
        """
        Resize image
        
        Args:
            image: Input image
            width: Target width
            height: Target height
            scale: Scale factor (if provided, width and height are ignored)
            interpolation: Interpolation method
            
        Returns:
            Resized image
        """
        if scale is not None:
            h, w = image.shape[:2]
            new_w = int(w * scale)
            new_h = int(h * scale)
        elif width is not None and height is not None:
            new_w = width
            new_h = height
        elif width is not None:
            h, w = image.shape[:2]
            aspect = width / w
            new_w = width
            new_h = int(h * aspect)
        elif height is not None:
            h, w = image.shape[:2]
            aspect = height / h
            new_w = int(w * aspect)
            new_h = height
        else:
            return image
            
        return cv2.resize(image, (new_w, new_h), interpolation=interpolation)
    
    @staticmethod
    def invert_image(image: np.ndarray) -> np.ndarray:
        """
        Invert image colors
        
        Args:
            image: Input image
            
        Returns:
            Inverted image
        """
        return cv2.bitwise_not(image)
    
    @staticmethod
    def apply_all_operations(image: np.ndarray, operations: Dict[str, Any]) -> np.ndarray:
        """
        Apply multiple image processing operations in sequence
        
        Args:
            image: Input image
            operations: Dictionary of operations and their parameters
            
        Returns:
            Processed image
        """
        result = image.copy()
        
        # Rotation
        if 'rotation' in operations:
            result = ImageProcessing.rotate_image(result, operations['rotation'])
        
        # Flip
        if operations.get('flip_horizontal', False):
            result = ImageProcessing.flip_horizontal(result)
        if operations.get('flip_vertical', False):
            result = ImageProcessing.flip_vertical(result)
        
        # Grayscale
        if operations.get('grayscale', False):
            result = ImageProcessing.to_grayscale(result)
        
        # Threshold
        if operations.get('threshold', False):
            threshold_value = operations.get('threshold_value', 128)
            result = ImageProcessing.apply_threshold(result, threshold_value)
        
        # Brightness/Contrast
        if 'brightness' in operations or 'contrast' in operations:
            brightness = operations.get('brightness', 0)
            contrast = operations.get('contrast', 1.0)
            result = ImageProcessing.adjust_brightness_contrast(result, brightness, contrast)
        
        # Gamma
        if 'gamma' in operations:
            result = ImageProcessing.apply_gamma_correction(result, operations['gamma'])
        
        # Saturation
        if 'saturation' in operations:
            result = ImageProcessing.adjust_saturation(result, operations['saturation'])
        
        # Blur
        if 'blur' in operations:
            kernel_size = operations.get('blur_kernel_size', 5)
            result = ImageProcessing.apply_gaussian_blur(result, kernel_size)
        
        # Sharpen
        if 'sharpen' in operations:
            strength = operations.get('sharpen_strength', 1.0)
            result = ImageProcessing.apply_sharpen(result, strength)
        
        # Histogram equalization
        if operations.get('histogram_equalization', False):
            result = ImageProcessing.apply_histogram_equalization(result)
        
        # Edge detection
        if operations.get('edge_detection', False):
            threshold1 = operations.get('edge_threshold1', 100)
            threshold2 = operations.get('edge_threshold2', 200)
            result = ImageProcessing.apply_canny_edge_detection(result, threshold1, threshold2)
        
        # Resize
        if 'resize' in operations:
            resize_params = operations['resize']
            result = ImageProcessing.resize_image(result, **resize_params)
        
        # Invert
        if operations.get('invert', False):
            result = ImageProcessing.invert_image(result)
        
        return result


def process_image_file(input_path: str, output_path: str, 
                      operations: Dict[str, Any]) -> bool:
    """
    Process an image file and save the result
    
    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        operations: Dictionary of operations to apply
        
    Returns:
        True if successful, False otherwise
    """
    try:
        image = cv2.imread(input_path)
        if image is None:
            logger.error(f"Failed to read image: {input_path}")
            return False
            
        processed = ImageProcessing.apply_all_operations(image, operations)
        cv2.imwrite(output_path, processed)
        logger.info(f"Processed image saved to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return False

