# 🎬 Vietnamese Story Audio to Video Generator

## START HERE! 👈

Welcome! This is a complete Python application that converts Vietnamese story MP3 audio files into beautiful TikTok-ready vertical videos using Google's Gemini AI.

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ Setup (2 minutes)

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2️⃣ Get API Key (1 minute)

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Create API Key"
3. Copy your key

### 3️⃣ Set API Key (30 seconds)

```bash
export GEMINI_API_KEY=your_api_key_here
```

### 4️⃣ Create Your First Video (1.5 minutes)

```bash
python main.py --audio story.mp3 --project my_story
```

**Done!** Your video is at: `projects/my_story/output/my_story_final.mp4`

---

## 📚 Documentation Guide

Choose what you need:

| Document | Purpose | Time |
|----------|---------|------|
| **This file** | Overview & quick start | 2 min |
| `QUICKSTART.md` | 5-minute quick start | 5 min |
| `README.md` | Complete documentation | 15 min |
| `INSTALLATION.md` | Detailed setup guide | 10 min |
| `API_REFERENCE.md` | Code examples & API | 20 min |
| `PROJECT_STRUCTURE.md` | Project organization | 10 min |

---

## 🎯 What This Does

### Input
- Vietnamese story MP3 audio file

### Process
1. **Audio Analysis** - Gemini AI transcribes and analyzes the audio
2. **Image Generation** - Creates AI images for each scene (9:16 vertical)
3. **Video Creation** - Combines images and audio into final MP4

### Output
- Professional TikTok-ready vertical video (540x960 pixels)
- All intermediate files organized in project folder
- Complete logs and metadata

---

## 📦 What's Included

### Core Application (7 files)
- `main.py` - Main entry point
- `step1_audio_analysis.py` - Audio analysis
- `step2_image_generation.py` - Image generation
- `step3_video_creation.py` - Video creation
- `example_usage.py` - Code examples
- `test_setup.py` - Setup verification
- `utils/` - Utility modules (logger, config)

### Documentation (6 files)
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick start guide
- `INSTALLATION.md` - Installation guide
- `PROJECT_STRUCTURE.md` - Project overview
- `API_REFERENCE.md` - API documentation
- `00_START_HERE.md` - This file!

### Configuration (3 files)
- `requirements.txt` - Python dependencies
- `config.yaml` - Advanced settings
- `setup.sh` - Automated setup

---

## 🚀 Usage Examples

### Basic Usage
```bash
python main.py --audio story.mp3 --project my_story
```

### With API Key (if not set as environment variable)
```bash
python main.py --audio story.mp3 --project my_story --api-key YOUR_KEY
```

### Verbose Mode (for debugging)
```bash
python main.py --audio story.mp3 --project my_story --verbose
```

### Programmatic Usage
```python
from main import StoryVideoGenerator

generator = StoryVideoGenerator("my_story", api_key)
video_path = generator.run("story.mp3")
print(f"Video created: {video_path}")
```

---

## ✅ Verify Installation

```bash
# Test setup
python test_setup.py
```

Expected output:
```
✓ Python 3.8+
✓ Virtual environment active
✓ Gemini API
✓ Pillow
✓ imageio
✓ FFmpeg installed
✓ GEMINI_API_KEY set
✓ All tests passed!
```

---

## [object Object], you'll get:

```
projects/my_story/
├── output/
│   └── my_story_final.mp4          # Your final video!
├── images/
│   ├── scene_001.png
│   ├── scene_002.png
│   └── ...
├── scripts/
│   ├── scripts.json                # Timestamped scripts
│   └── images_metadata.json        # Image metadata
└── logs/
    └── pipeline.log                # Execution log
```

---

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB for dependencies + project files
- **Internet**: Required for API calls
- **FFmpeg**: Required for video creation

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

---

## ⏱️ Performance

| Step | Time |
|------|------|
| Audio Analysis | 1-2 min |
| Image Generation | 2-5 min |
| Video Creation | 1-2 min |
| **Total** | **5-10 min** |

*Times vary based on audio length and system performance*

---

## 💰 Cost

Typical cost per video: **$0.15 - $0.60**

This depends on:
- Audio length
- Image quality
- API usage

Check [Google AI pricing](https://ai.google.dev/pricing) for current rates.

---

## [object Object]

### "FFmpeg not found"
```bash
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
```

### "API key not recognized"
```bash
# Check it's set
echo $GEMINI_API_KEY

# Or pass it directly
python main.py --audio story.mp3 --project my_story --api-key YOUR_KEY
```

### "No module named 'google'"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "Permission denied: './setup.sh'"
```bash
chmod +x setup.sh
./setup.sh
```

For more help, see `INSTALLATION.md`

---

## 💡 Tips for Best Results

✅ **Audio Quality**
- Use clear, high-quality MP3 (320 kbps)
- Ensure good Vietnamese pronunciation
- Keep audio under 10 minutes for faster processing

✅ **Scene Descriptions**
- Detailed descriptions generate better images
- Include cultural and costume details
- Describe lighting and atmosphere

✅ **Performance**
- Test with short audio first
- Monitor API usage
- Process during off-peak hours

---

## 🎓 Learning Path

### Beginner
1. Read this file (5 min)
2. Run `python test_setup.py` (2 min)
3. Create your first video (10 min)
4. Read `QUICKSTART.md` (5 min)

### Intermediate
1. Read `README.md` (15 min)
2. Review `example_usage.py` (10 min)
3. Try different audio files
4. Customize `config.yaml`

### Advanced
1. Read `API_REFERENCE.md` (20 min)
2. Review source code
3. Modify for custom use cases
4. Integrate into your applications

---

## 🎬 Next Steps

### Option 1: Quick Start (Recommended)
```bash
# 1. Setup
chmod +x setup.sh && ./setup.sh
source venv/bin/activate

# 2. Set API key
export GEMINI_API_KEY=your_key_here

# 3. Create video
python main.py --audio story.mp3 --project my_story

# 4. Check output
ls projects/my_story/output/
```

### Option 2: Detailed Setup
1. Read `INSTALLATION.md` for step-by-step instructions
2. Follow platform-specific setup
3. Verify with `python test_setup.py`
4. Create your first video

### Option 3: Programmatic Usage
1. Read `API_REFERENCE.md`
2. Review `example_usage.py`
3. Write your own Python code
4. Integrate into your application

---

## 📞 Support

### Documentation
- 📖 `README.md` - Complete guide
- ⚡ `QUICKSTART.md` - 5-minute start
- 🔧 `INSTALLATION.md` - Setup help
- 🏗️ `PROJECT_STRUCTURE.md` - Project overview
- 📚 `API_REFERENCE.md` - Code examples

### Debugging
- Check logs: `projects/your_project/logs/pipeline.log`
- Enable verbose: `--verbose` flag
- Run tests: `python test_setup.py`

### Common Issues
See `INSTALLATION.md` troubleshooting section

---

## 🌟 Features

✨ **Automatic Vietnamese Audio Analysis**
- Transcribe dialogue and narration
- Generate scene descriptions
- Create precise timestamps

🎨 **AI Image Generation**
- Create images matching scenes
- 9:16 vertical format (TikTok-ready)
- Cinematic quality

🎬 **Professional Video Creation**
- Combine images and audio
- Automatic timing sync
- H.264 encoded MP4

📊 **Project Organization**
- Automatic directory structure
- JSON metadata files
- Comprehensive logging

---

## 🎯 Common Use Cases

### Create TikTok Videos
```bash
python main.py --audio story.mp3 --project tiktok_video
# Upload to TikTok!
```

### Batch Process Multiple Stories
```bash
for file in *.mp3; do
  project=$(basename "$file" .mp3)
  python main.py --audio "$file" --project "$project"
done
```

### Integrate into Your App
```python
from main import StoryVideoGenerator

def create_video(audio_file, project_name, api_key):
    generator = StoryVideoGenerator(project_name, api_key)
    return generator.run(audio_file)
```

---

## 📋 Checklist

Before you start:

- [ ] Python 3.8+ installed
- [ ] FFmpeg installed
- [ ] Gemini API key obtained
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] API key set as environment variable
- [ ] Test setup passed (`python test_setup.py`)
- [ ] Vietnamese story MP3 ready

---

## 🎉 You're Ready!

Everything is set up and ready to go. 

### Your first command:
```bash
python main.py --audio story.mp3 --project my_first_video
```

### Then:
1. Wait 5-10 minutes for processing
2. Check `projects/my_first_video/output/my_first_video_final.mp4`
3. Upload to TikTok
4. Share and enjoy!

---

## 📚 Full Documentation Index

| File | Purpose |
|------|---------|
| `00_START_HERE.md` | Overview (this file) |
| `QUICKSTART.md` | 5-minute quick start |
| `README.md` | Complete documentation |
| `INSTALLATION.md` | Detailed setup guide |
| `API_REFERENCE.md` | Code examples & API |
| `PROJECT_STRUCTURE.md` | Project organization |
| `SETUP_COMPLETE.md` | Setup summary |

---

## 🚀 Ready to Create Amazing Videos?

Let's go! 🎬📱✨

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Set API key
export GEMINI_API_KEY=your_key_here

# 3. Create your video
python main.py --audio story.mp3 --project my_story

# 4. Enjoy!
```

---

**Questions?** Check the documentation files above.

**Issues?** See `INSTALLATION.md` troubleshooting section.

**Ready to code?** Check `API_REFERENCE.md` for examples.

---

**Happy storytelling! 🎬📱✨**

*Vietnamese Story Audio to Video Generator v1.0*

