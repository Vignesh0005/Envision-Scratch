"""
Additional Image Processing API Endpoints
Uses enhanced ImageProcessing utilities
"""

from flask import Blueprint, request, jsonify
from image_processing_utils import ImageProcessing, process_image_file
import cv2
import os
import logging

logger = logging.getLogger(__name__)

# Create blueprint for image processing routes
image_processing_bp = Blueprint('image_processing', __name__)


@image_processing_bp.route('/api/image/brightness-contrast', methods=['POST'])
def adjust_brightness_contrast():
    """Adjust brightness and contrast of an image"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        brightness = data.get('brightness', 0)
        contrast = data.get('contrast', 1.0)
        
        if not image_path or not os.path.exists(image_path):
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404

        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to read image'
            }), 500

        adjusted = ImageProcessing.adjust_brightness_contrast(img, brightness, contrast)
        
        directory = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_brightness_contrast{ext}"
        new_path = os.path.join(directory, new_filename)
        
        cv2.imwrite(new_path, adjusted, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        return jsonify({
            'status': 'success',
            'filepath': new_path
        })
        
    except Exception as e:
        logger.error(f"Error adjusting brightness/contrast: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@image_processing_bp.route('/api/image/gamma', methods=['POST'])
def apply_gamma():
    """Apply gamma correction to an image"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        gamma = data.get('gamma', 1.0)
        
        if not image_path or not os.path.exists(image_path):
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404

        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to read image'
            }), 500

        corrected = ImageProcessing.apply_gamma_correction(img, gamma)
        
        directory = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_gamma{ext}"
        new_path = os.path.join(directory, new_filename)
        
        cv2.imwrite(new_path, corrected, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        return jsonify({
            'status': 'success',
            'filepath': new_path
        })
        
    except Exception as e:
        logger.error(f"Error applying gamma correction: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@image_processing_bp.route('/api/image/saturation', methods=['POST'])
def adjust_saturation():
    """Adjust saturation of an image"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        saturation = data.get('saturation', 1.0)
        
        if not image_path or not os.path.exists(image_path):
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404

        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to read image'
            }), 500

        adjusted = ImageProcessing.adjust_saturation(img, saturation)
        
        directory = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_saturation{ext}"
        new_path = os.path.join(directory, new_filename)
        
        cv2.imwrite(new_path, adjusted, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        return jsonify({
            'status': 'success',
            'filepath': new_path
        })
        
    except Exception as e:
        logger.error(f"Error adjusting saturation: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@image_processing_bp.route('/api/image/histogram-equalization', methods=['POST'])
def apply_histogram_equalization():
    """Apply histogram equalization to an image"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        
        if not image_path or not os.path.exists(image_path):
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404

        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to read image'
            }), 500

        equalized = ImageProcessing.apply_histogram_equalization(img)
        
        directory = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_equalized{ext}"
        new_path = os.path.join(directory, new_filename)
        
        cv2.imwrite(new_path, equalized, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        return jsonify({
            'status': 'success',
            'filepath': new_path
        })
        
    except Exception as e:
        logger.error(f"Error applying histogram equalization: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@image_processing_bp.route('/api/image/process-multiple', methods=['POST'])
def process_multiple_operations():
    """Apply multiple image processing operations in sequence"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        operations = data.get('operations', {})
        
        if not image_path or not os.path.exists(image_path):
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404

        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to read image'
            }), 500

        processed = ImageProcessing.apply_all_operations(img, operations)
        
        directory = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_processed{ext}"
        new_path = os.path.join(directory, new_filename)
        
        cv2.imwrite(new_path, processed, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        return jsonify({
            'status': 'success',
            'filepath': new_path
        })
        
    except Exception as e:
        logger.error(f"Error processing multiple operations: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@image_processing_bp.route('/api/image/resize', methods=['POST'])
def resize_image():
    """Resize an image"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        width = data.get('width')
        height = data.get('height')
        scale = data.get('scale')
        
        if not image_path or not os.path.exists(image_path):
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404

        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to read image'
            }), 500

        resized = ImageProcessing.resize_image(img, width=width, height=height, scale=scale)
        
        directory = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_resized{ext}"
        new_path = os.path.join(directory, new_filename)
        
        cv2.imwrite(new_path, resized, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        return jsonify({
            'status': 'success',
            'filepath': new_path,
            'width': resized.shape[1],
            'height': resized.shape[0]
        })
        
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

