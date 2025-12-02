# Image Processing Utilities Integration

## Overview

Enhanced image processing utilities have been integrated into ENVISION, providing comprehensive image manipulation capabilities with improved rotation, brightness/contrast adjustment, gamma correction, saturation control, and more.

## Files Created

1. **`backend/image_processing_utils.py`** - Core image processing utilities class
2. **`backend/api_image_processing.py`** - Additional API endpoints for new operations

## Features

### Enhanced Operations

#### Rotation
- **Arbitrary Angle Rotation**: Rotate by any angle in degrees (not just 90°)
- **90° Rotation**: Optimized 90-degree rotation (clockwise/counterclockwise)
- **Smart Cropping**: Automatically adjusts canvas size to prevent cropping

#### Basic Operations
- **Flip**: Horizontal, vertical, or both
- **Grayscale**: Convert to grayscale (maintains 3-channel format)
- **Invert**: Color inversion
- **Threshold**: Binary thresholding with configurable threshold value

#### Advanced Adjustments
- **Brightness/Contrast**: Independent control of brightness (-100 to 100) and contrast (0.0 to 3.0)
- **Gamma Correction**: Gamma adjustment (0.1 to 3.0) for tone curve control
- **Saturation**: Color saturation adjustment (0.0 to 2.0)

#### Filters
- **Gaussian Blur**: Configurable kernel size
- **Sharpen**: Adjustable sharpening strength
- **Histogram Equalization**: Automatic contrast enhancement
- **Canny Edge Detection**: Configurable threshold values

#### Utilities
- **Resize**: By width, height, scale factor, or aspect ratio preservation
- **Batch Processing**: Apply multiple operations in sequence

## Integration with Existing Code

### Updated Endpoints

The following existing endpoints now use the enhanced utilities:

1. **`/api/rotate-image`**
   - Now supports arbitrary angle rotation via `angle` parameter
   - Falls back to 90° rotation if angle not provided
   - Uses `ImageProcessing.rotate_image()` or `rotate_image_90()`

2. **`/api/flip-image`**
   - Uses `ImageProcessing.flip_horizontal()`, `flip_vertical()`, or `flip_both()`
   - Supports 'both' direction for simultaneous horizontal and vertical flip

3. **`/api/grayscale`**
   - Uses `ImageProcessing.to_grayscale()`
   - Maintains 3-channel format for compatibility

### New API Endpoints

1. **`/api/image/brightness-contrast`** (POST)
   ```json
   {
     "imagePath": "/path/to/image.jpg",
     "brightness": 20,
     "contrast": 1.2
   }
   ```

2. **`/api/image/gamma`** (POST)
   ```json
   {
     "imagePath": "/path/to/image.jpg",
     "gamma": 1.5
   }
   ```

3. **`/api/image/saturation`** (POST)
   ```json
   {
     "imagePath": "/path/to/image.jpg",
     "saturation": 1.3
   }
   ```

4. **`/api/image/histogram-equalization`** (POST)
   ```json
   {
     "imagePath": "/path/to/image.jpg"
   }
   ```

5. **`/api/image/resize`** (POST)
   ```json
   {
     "imagePath": "/path/to/image.jpg",
     "width": 1920,
     "height": 1080
   }
   ```
   Or with scale:
   ```json
   {
     "imagePath": "/path/to/image.jpg",
     "scale": 0.5
   }
   ```

6. **`/api/image/process-multiple`** (POST)
   ```json
   {
     "imagePath": "/path/to/image.jpg",
     "operations": {
       "rotation": 45,
       "brightness": 10,
       "contrast": 1.1,
       "gamma": 1.2,
       "saturation": 1.15,
       "sharpen": true,
       "sharpen_strength": 1.0
     }
   }
   ```

## Usage Examples

### Python
```python
from image_processing_utils import ImageProcessing
import cv2

# Load image
img = cv2.imread('image.jpg')

# Rotate by arbitrary angle
rotated = ImageProcessing.rotate_image(img, 45)

# Adjust brightness and contrast
adjusted = ImageProcessing.adjust_brightness_contrast(img, brightness=20, contrast=1.2)

# Apply gamma correction
gamma_corrected = ImageProcessing.apply_gamma_correction(img, gamma=1.5)

# Apply multiple operations
operations = {
    'rotation': 30,
    'brightness': 15,
    'contrast': 1.1,
    'gamma': 1.2,
    'saturation': 1.15,
    'sharpen': True,
    'sharpen_strength': 1.0
}
processed = ImageProcessing.apply_all_operations(img, operations)
```

### JavaScript/API
```javascript
// Adjust brightness and contrast
fetch('http://localhost:5000/api/image/brightness-contrast', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    imagePath: '/path/to/image.jpg',
    brightness: 20,
    contrast: 1.2
  })
})
.then(res => res.json())
.then(data => console.log('Processed image:', data.filepath));

// Apply multiple operations
fetch('http://localhost:5000/api/image/process-multiple', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    imagePath: '/path/to/image.jpg',
    operations: {
      rotation: 45,
      brightness: 10,
      contrast: 1.1,
      gamma: 1.2,
      saturation: 1.15,
      sharpen: true,
      sharpen_strength: 1.0
    }
  })
})
.then(res => res.json())
.then(data => console.log('Processed image:', data.filepath));
```

## Available Operations Dictionary

When using `apply_all_operations()`, the operations dictionary can include:

```python
operations = {
    # Rotation
    'rotation': 45,  # Angle in degrees
    
    # Flip
    'flip_horizontal': True,
    'flip_vertical': True,
    
    # Color
    'grayscale': True,
    'invert': True,
    
    # Threshold
    'threshold': True,
    'threshold_value': 128,
    
    # Adjustments
    'brightness': 20,      # -100 to 100
    'contrast': 1.2,      # 0.0 to 3.0
    'gamma': 1.5,          # 0.1 to 3.0
    'saturation': 1.3,     # 0.0 to 2.0
    
    # Filters
    'blur': True,
    'blur_kernel_size': 5,
    'sharpen': True,
    'sharpen_strength': 1.0,
    'histogram_equalization': True,
    
    # Edge detection
    'edge_detection': True,
    'edge_threshold1': 100,
    'edge_threshold2': 200,
    
    # Resize
    'resize': {
        'width': 1920,
        'height': 1080
        # OR
        'scale': 0.5
    }
}
```

## Compatibility

- **Backward Compatible**: All existing endpoints continue to work
- **Enhanced Functionality**: Existing endpoints now have additional features
- **No Breaking Changes**: Default behavior remains the same

## Integration Points

1. **Existing Endpoints**: Enhanced with new utilities
2. **New Endpoints**: Additional operations via blueprint
3. **Module System**: Can be used by other analysis modules
4. **WebSocket Service**: Can be integrated for real-time processing

## Benefits

1. **More Control**: Arbitrary rotation angles, fine-tuned adjustments
2. **Better Quality**: Smart rotation with proper canvas adjustment
3. **Batch Processing**: Apply multiple operations efficiently
4. **Extensible**: Easy to add new operations
5. **Consistent API**: Unified interface for all operations

## Future Enhancements

- Real-time preview of adjustments
- Preset configurations
- Undo/redo functionality
- Processing history
- Performance optimizations for large images

