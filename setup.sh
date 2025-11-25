#!/bin/bash

# Vietnamese Story Audio to Video Generator - Setup Script

echo "=========================================="
echo "Vietnamese Story Video Generator Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check FFmpeg
echo ""
echo "Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg is installed"
    ffmpeg -version | head -n 1
else
    echo "⚠ FFmpeg not found. Install it with:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  CentOS/RHEL: sudo yum install ffmpeg"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the script:"
echo "  python main.py --audio <path_to_mp3> --project <project_name>"
echo ""
echo "Example:"
echo "  python main.py --audio story.mp3 --project my_story --api-key YOUR_API_KEY"
echo ""
echo "Or set the API key as environment variable:"
echo "  export GEMINI_API_KEY=your_api_key_here"
echo "  python main.py --audio story.mp3 --project my_story"
echo "=========================================="

