"""
Image Processing Module - Compatibility Alias
This module provides compatibility for imports expecting 'image_processing'
"""

# Import from the actual implementation
from image_processing_utils import ImageProcessing, ImageRotation, process_image_file

# Re-export everything for compatibility
__all__ = ['ImageProcessing', 'ImageRotation', 'process_image_file']

