# Quick Start Guide

Get up and running in 5 minutes!

## 1. Setup (2 minutes)

```bash
# Navigate to project directory
cd vietnamese_story_video

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

## 2. Get API Key (1 minute)

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Create API Key"
3. Copy your API key

## 3. Prepare Your Audio (1 minute)

- Have a Vietnamese story MP3 file ready
- Example: `story.mp3`

## 4. Run the Pipeline (1 minute)

```bash
# Set API key
export GEMINI_API_KEY=your_api_key_here

# Run the script
python main.py --audio story.mp3 --project my_story
```

## 5. Get Your Video!

Output video: `projects/my_story/output/my_story_final.mp4`

---

## Complete Example

```bash
# 1. Setup
cd vietnamese_story_video
chmod +x setup.sh
./setup.sh
source venv/bin/activate

# 2. Set API key
export GEMINI_API_KEY=AIzaSyD...

# 3. Run
python main.py --audio my_vietnamese_story.mp3 --project tiktok_video

# 4. Check output
ls -lh projects/tiktok_video/output/
```

## What Happens?

1. **Audio Analysis** (1-2 min)
   - Uploads MP3 to Gemini
   - Extracts Vietnamese dialogue
   - Generates scene descriptions
   - Creates timestamped scripts

2. **Image Generation** (2-5 min)
   - Creates AI images for each scene
   - 9:16 vertical format (TikTok-ready)
   - Saves as PNG files

3. **Video Creation** (1-2 min)
   - Combines images + audio
   - Creates MP4 video
   - Saves to output folder

**Total time: 5-10 minutes** (depending on audio length)

## Troubleshooting

**"FFmpeg not found"**
```bash
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
```

**"API key not recognized"**
```bash
# Check it's set
echo $GEMINI_API_KEY

# Or pass it directly
python main.py --audio story.mp3 --project my_story --api-key YOUR_KEY
```

**"No module named 'google'"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

- Check `README.md` for detailed documentation
- Explore `projects/my_story/` for generated files
- Try with different audio files
- Customize scene descriptions if needed

## Tips

✅ Use clear, detailed Vietnamese audio
✅ Keep audio under 10 minutes for faster processing
✅ Ensure good audio quality (320 kbps MP3)
✅ Check logs if something goes wrong: `projects/my_story/logs/pipeline.log`

---

**Ready to create amazing TikTok videos? Let's go! [object Object]

