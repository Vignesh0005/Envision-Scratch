from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import io
import base64
import os
import json
from datetime import datetime
import logging
from werkzeug.utils import secure_filename

# Import analysis modules
from modules.metallurgical_analysis import MetallurgicalAnalyzer
from modules.graphite_analysis import GraphiteAnalyzer
from modules.structural_analysis import StructuralAnalyzer
from modules.image_processing import ImageProcessor
from modules.camera_controller import CameraController
from modules.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS to allow requests from localhost:3000
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
}, supports_credentials=True)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Initialize modules
image_processor = ImageProcessor()
metallurgical_analyzer = MetallurgicalAnalyzer()
graphite_analyzer = GraphiteAnalyzer()
structural_analyzer = StructuralAnalyzer()
camera_controller = CameraController()
db_manager = DatabaseManager()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    """Get available camera devices"""
    try:
        cameras = camera_controller.get_available_cameras()
        return jsonify({
            'success': True,
            'cameras': cameras
        })
    except Exception as e:
        logger.error(f"Error getting cameras: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """Start camera capture"""
    try:
        data = request.get_json()
        camera_id = data.get('camera_id')
        settings = data.get('settings', {})
        
        success = camera_controller.start_camera(camera_id, settings)
        
        return jsonify({
            'success': success,
            'message': 'Camera started successfully' if success else 'Failed to start camera'
        })
    except Exception as e:
        logger.error(f"Error starting camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """Stop camera capture"""
    try:
        camera_controller.stop_camera()
        return jsonify({
            'success': True,
            'message': 'Camera stopped successfully'
        })
    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/camera/capture', methods=['POST'])
def capture_image():
    """Capture image from camera"""
    try:
        image_data = camera_controller.capture_image()
        if image_data is not None:
            # Save captured image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            cv2.imwrite(filepath, image_data)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Image captured successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to capture image'
            }), 400
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload image file"""
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if file:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Image uploaded successfully'
            })
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/processing/filters', methods=['POST'])
def apply_filters():
    """Apply image processing filters"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        filters = data.get('filters', [])
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename is required'
            }), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Image file not found'
            }), 404
        
        # Load and process image
        image = cv2.imread(filepath)
        processed_image = image_processor.apply_filters(image, filters)
        
        # Save processed image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_filename = f"processed_{timestamp}_{filename}"
        processed_filepath = os.path.join(app.config['RESULTS_FOLDER'], processed_filename)
        
        cv2.imwrite(processed_filepath, processed_image)
        
        return jsonify({
            'success': True,
            'original_filename': filename,
            'processed_filename': processed_filename,
            'message': 'Filters applied successfully'
        })
    except Exception as e:
        logger.error(f"Error applying filters: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis/metallurgical', methods=['POST'])
def analyze_metallurgical():
    """Perform metallurgical analysis"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        analysis_type = data.get('analysis_type', 'porosity')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename is required'
            }), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Image file not found'
            }), 404
        
        # Load image and perform analysis
        image = cv2.imread(filepath)
        
        if analysis_type == 'porosity':
            results = metallurgical_analyzer.analyze_porosity(image)
        elif analysis_type == 'phases':
            results = metallurgical_analyzer.analyze_phases(image)
        elif analysis_type == 'inclusions':
            results = metallurgical_analyzer.analyze_inclusions(image)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid analysis type'
            }), 400
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"metallurgical_{analysis_type}_{timestamp}_{filename}"
        results_filepath = os.path.join(app.config['RESULTS_FOLDER'], results_filename)
        
        cv2.imwrite(results_filepath, results['annotated_image'])
        
        # Save analysis data
        analysis_data = {
            'filename': filename,
            'analysis_type': analysis_type,
            'timestamp': timestamp,
            'results': results,
            'processed_image': results_filename
        }
        
        db_manager.save_analysis(analysis_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'processed_image': results_filename,
            'message': 'Metallurgical analysis completed successfully'
        })
    except Exception as e:
        logger.error(f"Error in metallurgical analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis/graphite', methods=['POST'])
def analyze_graphite():
    """Perform graphite analysis"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        analysis_type = data.get('analysis_type', 'nodularity')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename is required'
            }), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Image file not found'
            }), 404
        
        # Load image and perform analysis
        image = cv2.imread(filepath)
        
        if analysis_type == 'nodularity':
            results = graphite_analyzer.analyze_nodularity(image)
        elif analysis_type == 'flakes':
            results = graphite_analyzer.analyze_flakes(image)
        elif analysis_type == 'coating':
            results = graphite_analyzer.analyze_coating(image)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid analysis type'
            }), 400
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"graphite_{analysis_type}_{timestamp}_{filename}"
        results_filepath = os.path.join(app.config['RESULTS_FOLDER'], results_filename)
        
        cv2.imwrite(results_filepath, results['annotated_image'])
        
        # Save analysis data
        analysis_data = {
            'filename': filename,
            'analysis_type': analysis_type,
            'timestamp': timestamp,
            'results': results,
            'processed_image': results_filename
        }
        
        db_manager.save_analysis(analysis_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'processed_image': results_filename,
            'message': 'Graphite analysis completed successfully'
        })
    except Exception as e:
        logger.error(f"Error in graphite analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis/structural', methods=['POST'])
def analyze_structural():
    """Perform structural analysis"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        analysis_type = data.get('analysis_type', 'grain_size')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename is required'
            }), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Image file not found'
            }), 404
        
        # Load image and perform analysis
        image = cv2.imread(filepath)
        
        if analysis_type == 'grain_size':
            results = structural_analyzer.analyze_grain_size(image)
        elif analysis_type == 'dendritic':
            results = structural_analyzer.analyze_dendritic(image)
        elif analysis_type == 'particles':
            results = structural_analyzer.analyze_particles(image)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid analysis type'
            }), 400
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"structural_{analysis_type}_{timestamp}_{filename}"
        results_filepath = os.path.join(app.config['RESULTS_FOLDER'], results_filename)
        
        cv2.imwrite(results_filepath, results['annotated_image'])
        
        # Save analysis data
        analysis_data = {
            'filename': filename,
            'analysis_type': analysis_type,
            'timestamp': timestamp,
            'results': results,
            'processed_image': results_filename
        }
        
        db_manager.save_analysis(analysis_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'processed_image': results_filename,
            'message': 'Structural analysis completed successfully'
        })
    except Exception as e:
        logger.error(f"Error in structural analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calibration', methods=['POST'])
def calibrate_system():
    """Calibrate measurement system"""
    try:
        data = request.get_json()
        known_distance = data.get('known_distance')  # in microns
        pixel_count = data.get('pixel_count')
        
        if not known_distance or not pixel_count:
            return jsonify({
                'success': False,
                'error': 'Known distance and pixel count are required'
            }), 400
        
        pixel_size = known_distance / pixel_count
        
        # Save calibration data
        calibration_data = {
            'pixel_size': pixel_size,
            'known_distance': known_distance,
            'pixel_count': pixel_count,
            'timestamp': datetime.now().isoformat()
        }
        
        db_manager.save_calibration(calibration_data)
        
        return jsonify({
            'success': True,
            'pixel_size': pixel_size,
            'message': 'Calibration completed successfully'
        })
    except Exception as e:
        logger.error(f"Error in calibration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyses', methods=['GET'])
def get_analyses():
    """Get list of recent analyses"""
    try:
        analyses = db_manager.get_recent_analyses()
        return jsonify({
            'success': True,
            'analyses': analyses
        })
    except Exception as e:
        logger.error(f"Error getting analyses: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyses/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get specific analysis details"""
    try:
        analysis = db_manager.get_analysis(analysis_id)
        if analysis:
            return jsonify({
                'success': True,
                'analysis': analysis
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
