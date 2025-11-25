# Vietnamese Story Audio to Video Generator

Convert Vietnamese story MP3 audio files into engaging TikTok-style vertical videos with AI-generated scenes and images.

## Features

✨ **Three-Step Pipeline:**
1. **Audio Analysis** - Transcribe Vietnamese audio and generate timestamped scripts with scene descriptions using Gemini API
2. **Image Generation** - Create AI-generated images (9:16 aspect ratio) for each scene
3. **Video Creation** - Combine images and audio into a final MP4 video

🎯 **Key Capabilities:**
- Automatic Vietnamese audio transcription and analysis
- Scene-by-scene breakdown with precise timestamps
- AI-generated images matching scene descriptions
- Vertical video format (9:16) optimized for TikTok
- Seamless audio-image synchronization
- Project-based organization

## Prerequisites

- Python 3.8+
- FFmpeg (for video creation)
- Gemini API key (get it from [Google AI Studio](https://aistudio.google.com/))

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

### 1. Clone or download the project

```bash
cd vietnamese_story_video
```

### 2. Run setup script

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Set up Gemini API key

Get your API key from [Google AI Studio](https://aistudio.google.com/)

**Option A: Environment variable**
```bash
export GEMINI_API_KEY=your_api_key_here
```

**Option B: Command-line argument**
```bash
python main.py --audio story.mp3 --project my_story --api-key YOUR_API_KEY
```

## Usage

### Basic Usage

```bash
python main.py --audio story.mp3 --project my_story
```

### Full Example

```bash
# Activate virtual environment
source venv/bin/activate

# Run with environment variable
export GEMINI_API_KEY=your_api_key_here
python main.py --audio vietnamese_story.mp3 --project tiktok_video

# Or with command-line argument
python main.py --audio vietnamese_story.mp3 --project tiktok_video --api-key YOUR_API_KEY
```

### Command-line Options

```
usage: main.py [-h] --audio AUDIO --project PROJECT [--api-key API_KEY] [--verbose]

Options:
  --audio AUDIO          Path to input MP3 audio file (required)
  --project PROJECT      Project name for output directory (required)
  --api-key API_KEY      Gemini API key (or set GEMINI_API_KEY env var)
  --verbose              Enable verbose logging
  -h, --help            Show help message
```

## Output Structure

After running the script, your project directory will contain:

```
projects/
└── my_story/
    ├── output/
    │   └── my_story_final.mp4          # Final video
    ├── images/
    │   ├── scene_001.png
    │   ├── scene_002.png
    │   └── ...
    ├── scripts/
    │   ├── scripts.json                # Timestamped scripts
    │   └── images_metadata.json        # Image metadata
    └── logs/
        └── pipeline.log                # Execution logs
```

## Pipeline Details

### Step 1: Audio Analysis

- Uploads MP3 to Gemini API
- Uses `gemini-3.0-pro` for richer transcription (set `GEMINI_AUDIO_MODEL` to override)
- Extracts Vietnamese dialogue and narration
- Generates scene descriptions
- Creates timestamped script segments
- Output: `scripts/scripts.json`

**Output Format:**
```json
[
  {
    "script": "thủ đoạn thâm độc nhất để tiêu diệt 1 người là gì",
    "from": 0,
    "to": 3230,
    "scene": "2 người đàn ông mặc cổ trang đang cau mày, một người đàn ông đang thì thầm chuyện gì mờ ám vào tai người còn lại",
    "duration": 3230,
    "from_seconds": 0.0,
    "to_seconds": 3.23,
    "duration_seconds": 3.23
  },
  ...
]
```

### Step 2: Image Generation

- Uses Gemini to generate images based on scene descriptions
- Creates 9:16 vertical images (540x960 pixels)
- Maintains visual consistency between scenes
- Saves images as PNG files
- Output: `images/scene_*.png` and `scripts/images_metadata.json`

**Features:**
- Vivid, cinematic style
- Cultural and costume details
- Professional lighting and atmosphere
- Optimized for TikTok vertical format

### Step 3: Video Creation

- Combines images and audio using FFmpeg
- Synchronizes image duration with audio timestamps
- Creates H.264 encoded MP4 video
- Applies AAC audio codec
- Output: `output/project_name_final.mp4`

**Video Specifications:**
- Resolution: 540x960 (9:16 aspect ratio)
- Codec: H.264 (libx264)
- Audio: AAC
- Format: MP4

## Example Workflow

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Set API key
export GEMINI_API_KEY=sk-...

# 3. Run the pipeline
python main.py --audio my_story.mp3 --project tiktok_story

# 4. Check output
ls projects/tiktok_story/output/
# Output: tiktok_story_final.mp4

# 5. Upload to TikTok!
```

## Troubleshooting

### FFmpeg not found
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu/Debian
```

### API Key not recognized
```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Or pass it directly
python main.py --audio story.mp3 --project my_story --api-key YOUR_KEY
```

### Image generation fails
- Check API quota and rate limits
- Ensure scene descriptions are detailed enough
- Verify API key has image generation permissions

### Video creation fails
- Ensure FFmpeg is installed and in PATH
- Check that image files were created successfully
- Verify audio file is valid MP3

### Memory issues with large files
- Process shorter audio files first
- Increase system RAM or use a more powerful machine
- Consider splitting audio into multiple projects

## Performance Tips

1. **Faster Processing:**
   - Use shorter audio files (< 5 minutes)
   - Reduce image resolution if needed
   - Enable parallel processing if available

2. **Better Quality:**
   - Use high-quality input MP3 (320 kbps)
   - Provide detailed scene descriptions
   - Allow more time for image generation

3. **Cost Optimization:**
   - Monitor API usage on Google AI Studio
   - Batch process multiple stories
   - Reuse generated images when possible

## API Costs

Gemini API pricing varies. Check [Google AI Studio pricing](https://ai.google.dev/pricing) for current rates.

**Typical costs per video:**
- Audio analysis: ~$0.01-0.05
- Image generation: ~$0.10-0.50 (depending on quality)
- Total: ~$0.15-0.60 per video

## Limitations

- Audio must be in MP3 format
- Vietnamese language audio works best
- Image generation quality depends on scene descriptions
- Video duration limited by API quotas
- Requires internet connection for API calls

## Future Enhancements

- [ ] Support for multiple languages
- [ ] Batch processing multiple audio files
- [ ] Custom image styles and filters
- [ ] Advanced audio effects and transitions
- [ ] Subtitle generation
- [ ] Music and sound effects integration
- [ ] Web UI for easier usage
- [ ] Cloud processing support

## License

MIT License - Feel free to use and modify

## Support

For issues and questions:
1. Check the logs: `projects/your_project/logs/pipeline.log`
2. Enable verbose mode: `--verbose`
3. Review error messages carefully
4. Check FFmpeg installation

## Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.

## Disclaimer

This tool uses Google's Gemini API. Ensure you comply with:
- Google's Terms of Service
- Copyright and intellectual property laws
- Platform-specific guidelines (TikTok, etc.)

---

**Happy storytelling! 🎬📱**

