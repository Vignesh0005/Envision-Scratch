# ENVISION API Endpoints Reference

## Base URL
- **Development**: `http://localhost:5000`
- **Frontend**: `http://localhost:3000`

## All API Endpoints

### Camera Control

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/start-camera` | Start camera capture |
| POST | `/api/stop-camera` | Stop camera capture |
| GET | `/api/video-feed` | Get video stream (MJPEG) |
| POST | `/api/snapshot` | Take a snapshot |
| POST | `/api/set-camera-resolution` | Set camera resolution |

### Image Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/import-image` | Import/upload image |
| GET | `/api/get-image` | Get image by path |
| POST | `/api/list-images` | List all images |
| POST | `/api/delete-image` | Delete an image |
| GET | `/api/thumbnail` | Get image thumbnail |

### Image Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rotate-image` | Rotate image |
| POST | `/api/flip-image` | Flip image (horizontal/vertical) |
| POST | `/api/grayscale` | Convert to grayscale |
| POST | `/api/invert` | Invert image colors |
| POST | `/api/threshold` | Apply threshold |
| POST | `/api/lowpass-filter` | Apply lowpass filter |
| POST | `/api/median-filter` | Apply median filter |
| POST | `/api/edge-detect` | Edge detection |
| POST | `/api/edge-emphasis` | Edge emphasis |
| POST | `/api/image-sharpen` | Sharpen image |
| POST | `/api/image-splice` | Image splicing |
| POST | `/api/image-stitch` | Image stitching |
| POST | `/api/thin` | Image thinning |

### Image Processing (New Blueprint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/image/brightness-contrast` | Adjust brightness/contrast |
| POST | `/api/image/gamma` | Apply gamma correction |
| POST | `/api/image/saturation` | Adjust saturation |
| POST | `/api/image/histogram-equalization` | Histogram equalization |
| POST | `/api/image/resize` | Resize image |
| POST | `/api/image/process-multiple` | Apply multiple operations |

### Calibration

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/save-calibration` | Save calibration data |
| GET | `/api/get-calibrations` | Get all calibrations |

### Porosity Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/porosity/analyze` | Analyze porosity |
| POST | `/api/porosity/save-config` | Save porosity config |
| GET | `/api/porosity/load-config/<name>` | Load porosity config |
| POST | `/api/porosity/export-report` | Export porosity report |
| POST | `/api/porosity/get-histogram` | Get porosity histogram |
| POST | `/api/porosity/apply-intensity-threshold` | Apply intensity threshold |

### Phase Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/phase/analyze` | Analyze phase |
| POST | `/api/phase/save-configuration` | Save phase configuration |
| GET | `/api/phase/get-configurations` | Get all configurations |
| POST | `/api/phase/apply-configuration` | Apply configuration |

### Nodularity Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/nodularity/analyze` | Analyze nodularity |
| POST | `/api/nodularity/toggle-selection` | Toggle selection |
| POST | `/api/nodularity/set-cutoff` | Set cutoff value |
| POST | `/api/nodularity/update-sizes` | Update size ranges |
| POST | `/api/nodularity/export-report` | Export nodularity report |
| POST | `/api/nodularity/add-cumulative-result` | Add cumulative result |
| GET | `/api/nodularity/get-cumulative-results` | Get cumulative results |
| POST | `/api/nodularity/clear-cumulative-results` | Clear cumulative results |
| POST | `/api/nodularity/save-config` | Save nodularity config |
| GET | `/api/nodularity/load-config/<name>` | Load nodularity config |
| POST | `/api/nodularity/delete-config` | Delete nodularity config |
| POST | `/api/nodularity/transfer-to-phase-analysis` | Transfer to phase analysis |

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (React app)
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

## Common Issues

### Blank Screen Issues

1. **Check if server is running:**
   ```bash
   python run_all.py
   ```

2. **Check CORS in browser console:**
   - Open DevTools (F12)
   - Check Console for CORS errors
   - Check Network tab for failed requests

3. **Verify API endpoint exists:**
   ```bash
   python check_api_endpoints.py
   ```

4. **Check frontend API calls:**
   - Ensure frontend uses correct base URL: `http://localhost:5000`
   - Verify endpoint paths match backend routes

### Testing Endpoints

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test with CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:5000/api/health
```

## Notes

- All endpoints return JSON
- POST endpoints typically require JSON body
- Error responses include `status: 'error'` and `message` field
- Success responses include `status: 'success'`

