# ENVISION: Advanced Microscopy Image Analysis System

## Overview

**ENVISION** is a comprehensive, desktop-based microscopy image analysis platform designed specifically for materials science, metallurgy, and quality control applications. This integrated system combines cutting-edge computer vision algorithms with an intuitive user interface to provide researchers and quality control professionals with powerful tools for automated material characterization and analysis.

## Features

### 🎥 **Multi-Modal Camera Integration**
- Professional HIKROBOT microscopy camera support
- Standard webcam integration
- Real-time video streaming and high-resolution capture
- Automated calibration for accurate measurements

### 🔬 **Advanced Image Processing**
- **Spatial Domain Filters**: Gaussian blur, median filtering, edge detection
- **Morphological Operations**: Erosion, dilation, opening, closing
- **Transform Domain Processing**: Fourier-based filtering
- **Real-time Processing**: Immediate visual feedback

### 🧪 **Specialized Analysis Modules**
- **Metallurgical Analysis**: Porosity, phase segmentation, inclusion analysis
- **Graphite Analysis**: Nodularity assessment, flake classification
- **Structural Analysis**: Grain size, dendritic spacing, particle analysis

### 📏 **Measurement & Annotation System**
- Precise geometric measurements (lines, angles, areas)
- Calibrated measurements with micron-level accuracy
- Comprehensive reporting and data export

## Technology Stack

### Frontend
- **React.js 18.3.1** with modern hooks and functional components
- **Electron** for cross-platform desktop deployment
- **Tailwind CSS** for responsive and modern UI design
- **Fabric.js** for canvas-based drawing and measurement tools

### Backend
- **Python 3.8+** with Flask microservices architecture
- **OpenCV** for high-performance image processing
- **NumPy & SciPy** for scientific computing
- **scikit-image** for advanced image analysis algorithms
- **scikit-learn** for machine learning-based analysis

### Database
- **PostgreSQL** for data persistence and analysis results
- **SQLAlchemy** for database management
- **Alembic** for database migrations

## Installation

### Quick Start

For detailed installation instructions, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

### Prerequisites
- **Node.js 18+** and **npm 9+**
- **Python 3.8+** and **pip**
- **PostgreSQL 12+** (optional, for production)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Vignesh0005/Envision-Scratch.git
cd Envision-Scratch
```

### 2. Install Frontend Dependencies
```bash
npm install
```

### 3. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Install Camera SDKs (Required for Camera Features)

#### Hikrobot MVS SDK (Recommended - Already Integrated)
- Download from [Hikrobot MVS SDK](https://www.hikrobotics.com/en/machinevision/service/download)
- Install SDK to default location
- ENVISION automatically detects and uses the SDK

#### IDS uEye SDK (Optional)
- Download from [IDS Imaging](https://en.ids-imaging.com/downloads.html)
- Install SDK and Python bindings

#### Mshot SDK (Optional)
- Contact vendor for SDK
- Install according to vendor instructions

**Verify SDK Installation:**
```bash
cd backend
python check_camera_sdks.py
```

### 5. Database Setup (Optional)
```bash
# Create PostgreSQL database
createdb envision_microscopy

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost/envision_microscopy"
export FLASK_ENV=development
```

### 6. Initialize Database (Optional)
```bash
cd backend
python -c "from modules.database import DatabaseManager; db = DatabaseManager(); db.init_database()"
```

## Usage

### Development Mode

#### Start Backend Server
```bash
cd backend
python app.py
```
The Flask server will start on `http://localhost:5000`

#### Start Frontend Development Server
```bash
npm start
```
The React app will start on `http://localhost:3000`

#### Start Electron App
```bash
npm run electron-dev
```

### Production Build

#### Build React App
```bash
npm run build
```

#### Package Electron App
```bash
npm run dist
```

## Project Structure

```
Envision-Scratch/
├── public/                 # Static assets and Electron files
│   ├── electron.js        # Main Electron process
│   ├── preload.js         # Secure IPC communication
│   └── index.html         # Main HTML entry point
├── src/                   # React application source
│   ├── components/        # Reusable UI components
│   │   └── Layout/        # Application layout components
│   ├── pages/            # Application pages
│   ├── App.js            # Main React component
│   └── index.js          # React entry point
├── backend/               # Python backend server
│   ├── modules/          # Analysis and processing modules
│   ├── app.py            # Main Flask application
│   └── requirements.txt  # Python dependencies
├── package.json           # Node.js dependencies and scripts
├── tailwind.config.js    # Tailwind CSS configuration
└── README.md             # This file
```

## API Endpoints

### Camera Operations
- `GET /api/cameras` - Get available camera devices
- `POST /api/camera/start` - Start camera capture
- `POST /api/camera/stop` - Stop camera capture
- `POST /api/camera/capture` - Capture image from camera

### Image Processing
- `POST /api/upload` - Upload image file
- `POST /api/processing/filters` - Apply image processing filters

### Analysis
- `POST /api/analysis/metallurgical` - Perform metallurgical analysis
- `POST /api/analysis/graphite` - Perform graphite analysis
- `POST /api/analysis/structural` - Perform structural analysis

### System
- `GET /api/health` - Health check
- `POST /api/calibration` - Calibrate measurement system
- `GET /api/analyses` - Get recent analyses

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost/envision_microscopy

# Flask
FLASK_ENV=development
FLASK_DEBUG=1

# Camera
CAMERA_DEVICE_ID=default
CAMERA_RESOLUTION=1920x1080
CAMERA_FRAME_RATE=30
```

### Analysis Parameters
Each analysis module has configurable parameters that can be adjusted based on specific material types and analysis requirements. See individual module documentation for detailed parameter descriptions.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Guidelines

### Code Style
- **Frontend**: ESLint + Prettier configuration
- **Backend**: Black + Flake8 for Python code formatting
- **Commits**: Conventional commit messages

### Testing
```bash
# Frontend tests
npm test

# Backend tests
cd backend
pytest

# Integration tests
npm run test:integration
```

### Documentation
- Update README.md for user-facing changes
- Add docstrings for new Python functions
- Update API documentation for new endpoints

## Troubleshooting

### Common Issues

#### Camera Not Detected
- Ensure camera permissions are granted
- Check device manager for camera status
- Verify camera drivers are installed

#### Image Processing Errors
- Check image format compatibility
- Verify image file integrity
- Ensure sufficient memory for large images

#### Database Connection Issues
- Verify PostgreSQL service is running
- Check database credentials and permissions
- Ensure database exists and is accessible

### Performance Optimization
- Use appropriate image resolutions for analysis
- Implement batch processing for multiple images
- Optimize filter parameters for specific use cases

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation wiki

## Acknowledgments

- OpenCV community for computer vision algorithms
- scikit-image team for image processing tools
- React and Electron communities for desktop application framework
- Materials science researchers for domain expertise and testing

## Roadmap

### Version 1.1
- [ ] Cloud integration for remote analysis
- [ ] Mobile application for field analysis
- [ ] Advanced machine learning models

### Version 1.2
- [ ] Multi-language support
- [ ] Advanced reporting and visualization
- [ ] Integration with laboratory information systems

### Version 2.0
- [ ] AI-powered feature recognition
- [ ] Real-time collaboration features
- [ ] Advanced statistical analysis tools

---

**ENVISION** - Advancing Materials Science Through Intelligent Image Analysis
