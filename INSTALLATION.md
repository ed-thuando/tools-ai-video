# Installation Guide

Complete step-by-step installation instructions for all platforms.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: macOS 10.14+, Ubuntu 18.04+, Windows 10+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for dependencies + project files
- **Internet**: Required for API calls

### Recommended Requirements
- **OS**: macOS 11+, Ubuntu 20.04+, Windows 11
- **Python**: 3.10 or higher
- **RAM**: 16GB
- **Disk Space**: 10GB
- **GPU**: Optional (for faster image generation)

## Prerequisites

### 1. Python Installation

**macOS:**
```bash
# Using Homebrew
brew install python3

# Verify installation
python3 --version
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip

# Verify installation
python3 --version
```

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✓ Check "Add Python to PATH"
4. Click "Install Now"

Verify:
```cmd
python --version
```

### 2. FFmpeg Installation

**macOS (Homebrew):**
```bash
brew install ffmpeg

# Verify
ffmpeg -version
```

**macOS (MacPorts):**
```bash
sudo port install ffmpeg

# Verify
ffmpeg -version
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg

# Verify
ffmpeg -version
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg

# Verify
ffmpeg -version
```

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add to PATH:
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Add `C:\ffmpeg\bin` to PATH
4. Verify in Command Prompt:
   ```cmd
   ffmpeg -version
   ```

### 3. Git (Optional but Recommended)

**macOS:**
```bash
brew install git
```

**Ubuntu/Debian:**
```bash
sudo apt-get install git
```

**Windows:**
Download from [git-scm.com](https://git-scm.com/download/win)

## Installation Steps

### Step 1: Clone or Download Project

**Using Git:**
```bash
git clone <repository-url>
cd vietnamese_story_video
```

**Or download ZIP:**
1. Download ZIP from repository
2. Extract to desired location
3. Open terminal/command prompt in that directory

### Step 2: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### Step 3: Upgrade pip

**All platforms:**
```bash
pip install --upgrade pip setuptools wheel
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-generativeai` - Gemini API client
- `Pillow` - Image processing
- `imageio` - Video processing
- `pydub` - Audio processing
- Other utilities

### Step 5: Verify Installation

```bash
# Check Python packages
pip list | grep -E "google|Pillow|imageio|pydub"

# Check FFmpeg
ffmpeg -version

# Check virtual environment
which python  # macOS/Linux
where python  # Windows
```

## Verification

### Test Installation

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Test imports
python -c "import google.generativeai; print('✓ Gemini API OK')"
python -c "import PIL; print('✓ Pillow OK')"
python -c "import imageio; print('✓ imageio OK')"

# Test FFmpeg
ffmpeg -version | head -1
```

### Run Help Command

```bash
python main.py --help
```

Expected output:
```
usage: main.py [-h] --audio AUDIO --project PROJECT [--api-key API_KEY] [--verbose]

Vietnamese Story Audio to Video Generator
...
```

## Configuration

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Create API Key"
3. Copy the generated key
4. Keep it secure!

### 2. Set Environment Variable

**macOS/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export GEMINI_API_KEY=your_api_key_here

# Apply changes
source ~/.bashrc  # or ~/.zshrc
```

**Windows (Command Prompt):**
```cmd
setx GEMINI_API_KEY your_api_key_here
```

**Windows (PowerShell):**
```powershell
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_api_key_here", "User")
```

### 3. Verify API Key

```bash
echo $GEMINI_API_KEY  # macOS/Linux
echo %GEMINI_API_KEY%  # Windows
```

## First Run

### Quick Test

```bash
# Activate virtual environment
source venv/bin/activate

# Run with test audio (if available)
python main.py --audio test_story.mp3 --project test_run --api-key YOUR_API_KEY
```

### Expected Output

```
2024-01-15 10:30:45 - main - INFO - Initialized StoryVideoGenerator for project: test_run
============================================================
STEP 1: Analyzing audio and generating scripts...
============================================================
2024-01-15 10:30:46 - step1_audio_analysis - INFO - Analyzing audio file: test_story.mp3
...
✓ Video generation completed successfully!
Output video: projects/test_run/output/test_run_final.mp4
============================================================
```

## Troubleshooting

### Virtual Environment Issues

**Problem:** `command not found: venv`

**Solution:**
```bash
# macOS/Linux
python3 -m venv venv

# Windows
python -m venv venv
```

### Python Version Issues

**Problem:** `Python 3.7 or lower detected`

**Solution:**
```bash
# Check version
python3 --version

# Install Python 3.8+
brew install python3  # macOS
sudo apt-get install python3.10  # Ubuntu
# Download from python.org  # Windows
```

### FFmpeg Not Found

**Problem:** `ffmpeg: command not found`

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Windows - Add to PATH manually
# See FFmpeg Installation section above
```

### Pip Install Fails

**Problem:** `ERROR: Could not find a version that satisfies the requirement`

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Clear cache
pip cache purge

# Try again
pip install -r requirements.txt
```

### API Key Not Working

**Problem:** `API key not recognized`

**Solution:**
1. Verify key is correct: `echo $GEMINI_API_KEY`
2. Check key hasn't expired on [Google AI Studio](https://aistudio.google.com/)
3. Try passing key directly: `--api-key YOUR_KEY`
4. Check for extra spaces or quotes

### Permission Denied

**Problem:** `Permission denied: './setup.sh'`

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### Memory Issues

**Problem:** `MemoryError` or `Out of memory`

**Solution:**
- Close other applications
- Process shorter audio files
- Increase system RAM
- Use a machine with more resources

### Slow Performance

**Problem:** Script runs very slowly

**Solution:**
- Check internet connection
- Reduce image quality in config
- Use faster GPU if available
- Process shorter audio files

## Uninstallation

### Remove Virtual Environment

```bash
# Deactivate first
deactivate

# Remove directory
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

### Remove Project

```bash
cd ..
rm -rf vietnamese_story_video  # macOS/Linux
rmdir /s vietnamese_story_video  # Windows
```

## Next Steps

1. Read [QUICKSTART.md](QUICKSTART.md) for quick start
2. Check [README.md](README.md) for detailed documentation
3. Review [example_usage.py](example_usage.py) for code examples
4. Run your first video: `python main.py --audio story.mp3 --project my_story`

## Support

If you encounter issues:

1. Check logs: `projects/your_project/logs/pipeline.log`
2. Enable verbose mode: `--verbose`
3. Review error messages
4. Check this troubleshooting section
5. Review [README.md](README.md) FAQ

---

**Installation complete! Ready to create amazing videos![object Object]
