# IDS uEye SDK Download Guide

## Quick Guide for IDS uEye SDK Download

When downloading from [IDS Imaging website](https://en.ids-imaging.com/downloads.html), here's what to select:

### Step-by-Step Selection

#### 1. **Product Family**
- Select: **"uEye"** or **"uEye USB"** or **"uEye GigE"**
- This is the main camera series from IDS

#### 2. **Model** (if asked)
- If you have a specific camera model, select it
- If unsure, select: **"All Models"** or **"Generic"**
- Common models: uEye CP, uEye LE, uEye SE, etc.

#### 3. **Interface Type**
- **"USB 2.0"** or **"USB 3.0"** - For USB cameras
- **"GigE"** or **"Ethernet"** - For network cameras
- **"USB 2.0 / USB 3.0"** - If you have both types

#### 4. **Operating System**
- **"Windows"** - Select your Windows version (10/11)
- **"64-bit"** - For most modern systems

#### 5. **SDK Version**
- Select: **"Latest Version"** or **"uEye SDK"**
- Usually something like "uEye SDK 4.96" or similar

### Recommended Selections (If Unsure)

If you're not sure about your camera:

1. **Product Family**: `uEye` (or `All`)
2. **Model**: `All Models` or `Generic`
3. **Interface**: 
   - If USB camera: `USB 3.0` (most common) or `USB 2.0 / USB 3.0`
   - If network camera: `GigE` or `Ethernet`
4. **OS**: `Windows 10/11 64-bit`
5. **SDK**: `uEye SDK` (latest version)

### What You're Downloading

You're downloading the **uEye SDK** which includes:
- `ueye_api.dll` - The main DLL file needed
- Camera drivers
- Development tools
- Documentation

### After Download

1. Run the installer
2. Install to default location: `C:\Program Files\IDS\uEye\`
3. The DLL will be in: `C:\Program Files\IDS\uEye\Develop\Bin64\ueye_api.dll`
4. Verify with: `python check_ids_sdk.py`

### Alternative: Minimal Installation

If you only need the DLL file:
- Look for "Runtime" or "Redistributable" package
- This contains just the DLL without full SDK

### Troubleshooting

**Can't find the right option?**
- Select the most generic options (All Models, All Interfaces)
- Download the full SDK package
- It will work with all IDS cameras

**Multiple downloads available?**
- Choose the **"Windows SDK"** or **"Development Package"**
- Avoid "Linux" or "macOS" versions

### Quick Checklist

- [ ] Product Family: uEye
- [ ] Model: All Models (or your specific model)
- [ ] Interface: USB 3.0 (or your camera type)
- [ ] OS: Windows 64-bit
- [ ] SDK: Latest uEye SDK version
- [ ] Download and install
- [ ] Verify DLL location
- [ ] Test with `python check_ids_sdk.py`

---

**Note**: If you're not using IDS cameras, you don't need to download this. Your Hikrobot setup is already complete!

