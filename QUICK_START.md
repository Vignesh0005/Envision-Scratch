# ENVISION Quick Start Guide

Get ENVISION up and running in minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python --version

# Check Node.js version (need 18+)
node --version

# Check npm version (need 9+)
npm --version
```

## 5-Minute Setup

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Install Hikrobot SDK (Required for Camera)

1. Download MVS SDK from [Hikrobot website](https://www.hikrobotics.com/en/machinevision/service/download)
2. Install to default location
3. Verify installation:

```bash
cd backend
python check_camera_sdks.py
```

Should show: `HIKROBOT : ✓ Available`

### Step 3: Start the Server

```bash
cd backend
python start_server.py
```

Server starts on `http://localhost:5000`

### Step 4: Start Frontend (Optional)

In a new terminal:

```bash
npm install
npm start
```

Frontend runs on `http://localhost:3000`

## Verify Installation

### Test Camera Service

```bash
cd backend
python start_websocket_service.py
```

In another terminal:

```bash
cd backend/examples
python quick_start_example.py
```

### Test Image Processing

```bash
cd backend/examples
python quick_start_example.py
```

## What's Next?

- **Full Installation**: See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- **Camera Setup**: Configure your camera in the application
- **Calibration**: Set up measurement calibration
- **Examples**: Explore `backend/examples/` directory

## Troubleshooting

**Problem**: `pip install` fails
- Solution: Update pip: `python -m pip install --upgrade pip`

**Problem**: Camera SDK not found
- Solution: Run `python check_camera_sdks.py` to diagnose

**Problem**: Port already in use
- Solution: Change port in `camera_config.py` or stop conflicting service

For more help, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

