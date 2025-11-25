# Project Structure

Complete overview of the Vietnamese Story Video Generator project structure.

## Directory Layout

```
vietnamese_story_video/
├── main.py                          # Main entry point
├── step1_audio_analysis.py          # Audio analysis module
├── step2_image_generation.py        # Image generation module
├── step3_video_creation.py          # Video creation module
├── example_usage.py                 # Usage examples
├── test_setup.py                    # Setup verification script
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── logger.py                    # Logging configuration
│   └── config.py                    # Configuration management
│
├── projects/                        # Generated projects (created at runtime)
│   └── {project_name}/
│       ├── output/                  # Final video output
│       │   └── {project_name}_final.mp4
│       ├── images/                  # Generated scene images
│       │   ├── scene_001.png
│       │   ├── scene_002.png
│       │   └── ...
│       ├── scripts/                 # Analysis results
│       │   ├── scripts.json         # Timestamped scripts
│       │   └── images_metadata.json # Image metadata
│       └── logs/                    # Execution logs
│           └── pipeline.log
│
├── venv/                            # Virtual environment (created by setup)
│
├── requirements.txt                 # Python dependencies
├── setup.sh                         # Setup script
├── config.yaml                      # Configuration file
│
├── README.md                        # Main documentation
├── QUICKSTART.md                    # Quick start guide
├── INSTALLATION.md                  # Installation guide
├── PROJECT_STRUCTURE.md             # This file
│
└── .gitignore                       # Git ignore rules
```

## File Descriptions

### Core Modules

#### `main.py`
- **Purpose**: Main orchestrator and CLI entry point
- **Key Classes**: `StoryVideoGenerator`
- **Functions**:
  - `run()`: Execute complete pipeline
  - `main()`: CLI argument parsing and execution
- **Usage**: `python main.py --audio story.mp3 --project my_story`

#### `step1_audio_analysis.py`
- **Purpose**: Analyze audio and generate timestamped scripts
- **Key Classes**: `AudioAnalyzer`
- **Functions**:
  - `analyze()`: Main analysis function
  - `_encode_audio()`: Convert MP3 to base64
  - `_validate_and_normalize()`: Validate script data
- **Output**: List of script segments with timestamps and scene descriptions

#### `step2_image_generation.py`
- **Purpose**: Generate AI images for each scene
- **Key Classes**: `ImageGenerator`
- **Functions**:
  - `generate()`: Generate images for all scenes
  - `_create_image_prompt()`: Create enhanced prompts
  - `_generate_image()`: Generate single image
  - `_create_placeholder_image()`: Create test images
- **Output**: PNG images (540x960 pixels, 9:16 aspect ratio)

#### `step3_video_creation.py`
- **Purpose**: Combine images and audio into final video
- **Key Classes**: `VideoCreator`
- **Functions**:
  - `create()`: Main video creation function
  - `_create_concat_file()`: Create FFmpeg concat file
  - `_create_video_with_ffmpeg()`: Use FFmpeg to create video
  - `_create_video_with_imageio()`: Fallback video creation
- **Output**: MP4 video file

### Utility Modules

#### `utils/logger.py`
- **Purpose**: Logging configuration
- **Functions**:
  - `setup_logger()`: Configure logger with console and file output
- **Features**:
  - Colored console output
  - File logging
  - Debug and info levels

#### `utils/config.py`
- **Purpose**: Project configuration and directory management
- **Key Classes**: `Config`
- **Functions**:
  - `setup_directories()`: Create project directories
  - `save_scripts()`: Save script data to JSON
  - `save_images_metadata()`: Save image metadata
  - `get_project_info()`: Get project information
- **Features**:
  - Automatic directory creation
  - JSON file management
  - Project organization

### Configuration Files

#### `requirements.txt`
- Lists all Python package dependencies
- Install with: `pip install -r requirements.txt`

#### `config.yaml`
- YAML configuration file for advanced settings
- Includes:
  - API settings
  - Image specifications
  - Video encoding options
  - Processing parameters
  - Logging configuration

#### `.gitignore`
- Specifies files to ignore in version control
- Excludes:
  - Virtual environment (`venv/`)
  - Generated projects (`projects/`)
  - Cache files (`__pycache__/`)
  - Environment files (`.env`)

### Documentation

#### `README.md`
- Complete project documentation
- Features, usage, troubleshooting
- API information and examples

#### `QUICKSTART.md`
- 5-minute quick start guide
- Basic setup and first run
- Common issues and solutions

#### `INSTALLATION.md`
- Detailed installation instructions
- Platform-specific guides
- Dependency installation
- Troubleshooting guide

#### `PROJECT_STRUCTURE.md`
- This file
- Project organization overview
- File descriptions

### Scripts

#### `setup.sh`
- Automated setup script
- Creates virtual environment
- Installs dependencies
- Checks FFmpeg installation

#### `example_usage.py`
- Practical usage examples
- 4 different usage patterns
- Batch processing example
- Custom configuration example

#### `test_setup.py`
- Verification script
- Tests Python version
- Checks dependencies
- Verifies FFmpeg
- Validates API key setup

## Data Flow

```
Input MP3
    ↓
[Step 1: Audio Analysis]
    ↓
scripts.json (timestamped scripts + scene descriptions)
    ↓
[Step 2: Image Generation]
    ↓
scene_001.png, scene_002.png, ... (9:16 images)
    ↓
[Step 3: Video Creation]
    ↓
Output MP4 Video
```

## Generated Project Structure

When you run the script with `--project my_story`, it creates:

```
projects/my_story/
├── output/
│   └── my_story_final.mp4          # Final video
├── images/
│   ├── scene_001.png               # Scene 1 image
│   ├── scene_002.png               # Scene 2 image
│   └── ...
├── scripts/
│   ├── scripts.json                # Timestamped scripts
│   └── images_metadata.json        # Image metadata
└── logs/
    └── pipeline.log                # Execution log
```

## Key Data Structures

### Script Data (scripts.json)
```json
[
  {
    "script": "Vietnamese dialogue",
    "from": 0,
    "to": 3230,
    "scene": "Scene description",
    "duration": 3230,
    "from_seconds": 0.0,
    "to_seconds": 3.23,
    "duration_seconds": 3.23
  }
]
```

### Image Metadata (images_metadata.json)
```json
[
  {
    "index": 1,
    "from": 0,
    "to": 3230,
    "duration": 3.23,
    "duration_ms": 3230,
    "from_seconds": 0.0,
    "to_seconds": 3.23,
    "duration_seconds": 3.23,
    "scene_description": "Scene description",
    "script": "Vietnamese dialogue",
    "image_path": "/path/to/scene_001.png",
    "image_filename": "scene_001.png"
  }
]
```

## Dependencies

### Core Dependencies
- `google-generativeai`: Gemini API client
- `Pillow`: Image processing
- `imageio`: Video processing
- `pydub`: Audio processing

### System Dependencies
- `FFmpeg`: Video encoding and processing
- `Python 3.8+`: Runtime environment

## Configuration Hierarchy

1. **Default values** in code
2. **config.yaml** (if present)
3. **Environment variables**
4. **Command-line arguments** (highest priority)

## Logging

Logs are saved to: `projects/{project_name}/logs/pipeline.log`

Log levels:
- `DEBUG`: Detailed information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## Performance Considerations

### Memory Usage
- Audio analysis: ~50-100 MB
- Image generation: ~200-500 MB per image
- Video creation: ~100-200 MB

### Processing Time
- Audio analysis: 1-2 minutes
- Image generation: 2-5 minutes (per image)
- Video creation: 1-2 minutes
- **Total**: 5-10 minutes for typical 3-5 minute audio

### Optimization Tips
- Use shorter audio files
- Reduce image resolution if needed
- Enable parallel processing
- Use SSD for faster I/O

## Extension Points

### Custom Image Generator
Modify `step2_image_generation.py` to use different image generation APIs

### Custom Video Encoder
Modify `step3_video_creation.py` to use different video encoding options

### Custom Audio Analyzer
Modify `step1_audio_analysis.py` to support different languages or audio formats

### Custom Configuration
Extend `utils/config.py` to add custom configuration options

## Error Handling

Each module includes:
- Input validation
- Error logging
- Graceful error handling
- Informative error messages

## Testing

Run setup verification:
```bash
python test_setup.py
```

Run examples:
```bash
python example_usage.py
```

## Version Control

Recommended `.gitignore` entries:
```
venv/
projects/
__pycache__/
*.pyc
.env
.DS_Store
*.log
```

## Future Enhancements

- [ ] Web UI
- [ ] Batch processing
- [ ] Custom styles
- [ ] Subtitle generation
- [ ] Multi-language support
- [ ] Cloud processing
- [ ] Advanced effects

---

**Project Structure Complete! Ready to generate amazing videos! 🎬**

