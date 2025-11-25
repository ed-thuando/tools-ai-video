# API Reference

Complete API documentation for the Vietnamese Story Video Generator.

## Table of Contents

1. [Main Module](#main-module)
2. [Audio Analysis Module](#audio-analysis-module)
3. [Image Generation Module](#image-generation-module)
4. [Video Creation Module](#video-creation-module)
5. [Utility Modules](#utility-modules)
6. [Data Structures](#data-structures)

---

## Main Module

### `StoryVideoGenerator`

Main orchestrator class for the complete pipeline.

#### Constructor

```python
StoryVideoGenerator(project_name: str, api_key: str)
```

**Parameters:**
- `project_name` (str): Name of the project (used for output directory)
- `api_key` (str): Gemini API key

**Example:**
```python
from main import StoryVideoGenerator

generator = StoryVideoGenerator(
    project_name="my_story",
    api_key="AIzaSyD..."
)
```

#### Methods

##### `run(audio_path: str) -> str`

Execute the complete pipeline.

**Parameters:**
- `audio_path` (str): Path to input MP3 file

**Returns:**
- (str): Path to generated video file

**Raises:**
- `FileNotFoundError`: If audio file doesn't exist
- `ValueError`: If audio file is not MP3
- `Exception`: If any pipeline step fails

**Example:**
```python
video_path = generator.run("story.mp3")
print(f"Video created: {video_path}")
```

---

## Audio Analysis Module

### `AudioAnalyzer`

Analyzes audio and generates timestamped scripts.

#### Constructor

```python
AudioAnalyzer(api_key: str)
```

**Parameters:**
- `api_key` (str): Gemini API key

**Example:**
```python
from step1_audio_analysis import AudioAnalyzer

analyzer = AudioAnalyzer(api_key="AIzaSyD...")
```

#### Methods

##### `analyze(audio_path: str) -> List[Dict]`

Analyze audio and generate timestamped scripts.

**Parameters:**
- `audio_path` (str): Path to MP3 file

**Returns:**
- (List[Dict]): List of script segments with timestamps

**Raises:**
- `FileNotFoundError`: If audio file doesn't exist
- `ValueError`: If response parsing fails

**Example:**
```python
scripts = analyzer.analyze("story.mp3")
for script in scripts:
    print(f"{script['from']:.2f}s - {script['to']:.2f}s: {script['script']}")
```

**Output Structure:**
```python
[
    {
        "script": "Vietnamese dialogue",
        "from": 0.0,           # Start time in seconds
        "to": 3.23,            # End time in seconds
        "scene": "Scene description",
        "duration": 3.23       # Duration in seconds
    },
    ...
]
```

---

## Image Generation Module

### `ImageGenerator`

Generates AI images for each scene.

#### Constructor

```python
ImageGenerator(api_key: str)
```

**Parameters:**
- `api_key` (str): Gemini API key

**Example:**
```python
from step2_image_generation import ImageGenerator

generator = ImageGenerator(api_key="AIzaSyD...")
```

#### Methods

##### `generate(scripts_data: List[Dict], output_dir: str) -> List[Dict]`

Generate images for each scene.

**Parameters:**
- `scripts_data` (List[Dict]): List of script segments from Step 1
- `output_dir` (str): Directory to save generated images

**Returns:**
- (List[Dict]): List of image metadata

**Raises:**
- `Exception`: If image generation fails

**Example:**
```python
images = generator.generate(scripts_data, "projects/my_story/images")
for image in images:
    print(f"Scene {image['index']}: {image['image_path']}")
```

**Output Structure:**
```python
[
    {
        "index": 1,
        "from": 0.0,
        "to": 3.23,
        "duration": 3.23,
        "scene_description": "Scene description",
        "script": "Vietnamese dialogue",
        "image_path": "/path/to/scene_001.png",
        "image_filename": "scene_001.png"
    },
    ...
]
```

---

## Video Creation Module

### `VideoCreator`

Creates final video by combining images and audio.

#### Constructor

```python
VideoCreator()
```

**Example:**
```python
from step3_video_creation import VideoCreator

creator = VideoCreator()
```

#### Methods

##### `create(audio_path: str, scripts_data: List[Dict], images_data: List[Dict], output_dir: str, project_name: str) -> str`

Create final video.

**Parameters:**
- `audio_path` (str): Path to input audio file
- `scripts_data` (List[Dict]): Script data from Step 1
- `images_data` (List[Dict]): Image data from Step 2
- `output_dir` (str): Directory to save output video
- `project_name` (str): Project name (used in filename)

**Returns:**
- (str): Path to generated video file

**Raises:**
- `RuntimeError`: If FFmpeg fails
- `FileNotFoundError`: If output file not created

**Example:**
```python
video_path = creator.create(
    audio_path="story.mp3",
    scripts_data=scripts,
    images_data=images,
    output_dir="projects/my_story/output",
    project_name="my_story"
)
print(f"Video: {video_path}")
```

---

## Utility Modules

### `utils.logger`

#### `setup_logger(name: str, log_file: str = None) -> logging.Logger`

Setup logger with console and optional file output.

**Parameters:**
- `name` (str): Logger name (usually `__name__`)
- `log_file` (str, optional): Path to log file

**Returns:**
- (logging.Logger): Configured logger instance

**Example:**
```python
from utils.logger import setup_logger

logger = setup_logger(__name__, "logs/app.log")
logger.info("Application started")
```

### `utils.config`

#### `Config`

Project configuration and directory management.

##### Constructor

```python
Config(project_name: str)
```

**Parameters:**
- `project_name` (str): Name of the project

**Example:**
```python
from utils.config import Config

config = Config("my_story")
config.setup_directories()
```

##### Methods

###### `setup_directories()`

Create all necessary project directories.

**Example:**
```python
config.setup_directories()
# Creates:
# - projects/my_story/
# - projects/my_story/output/
# - projects/my_story/images/
# - projects/my_story/scripts/
# - projects/my_story/logs/
```

###### `save_scripts(scripts_data: List[Dict]) -> str`

Save scripts data to JSON file.

**Parameters:**
- `scripts_data` (List[Dict]): Script data to save

**Returns:**
- (str): Path to saved file

**Example:**
```python
scripts_file = config.save_scripts(scripts_data)
print(f"Scripts saved to: {scripts_file}")
```

###### `save_images_metadata(images_data: List[Dict]) -> str`

Save images metadata to JSON file.

**Parameters:**
- `images_data` (List[Dict]): Image metadata to save

**Returns:**
- (str): Path to saved file

**Example:**
```python
metadata_file = config.save_images_metadata(images_data)
print(f"Metadata saved to: {metadata_file}")
```

###### `get_project_info() -> Dict`

Get project information.

**Returns:**
- (Dict): Project information dictionary

**Example:**
```python
info = config.get_project_info()
print(f"Project: {info['project_name']}")
print(f"Output: {info['output_dir']}")
```

---

## Data Structures

### Script Data

```python
{
    "script": str,          # Vietnamese dialogue/narration
    "from": float,          # Start time in seconds
    "to": float,            # End time in seconds
    "scene": str,           # Scene description in Vietnamese
    "duration": float       # Duration in seconds (to - from)
}
```

### Image Metadata

```python
{
    "index": int,                   # Scene index (1-based)
    "from": float,                  # Start time in seconds
    "to": float,                    # End time in seconds
    "duration": float,              # Duration in seconds
    "scene_description": str,       # Scene description
    "script": str,                  # Vietnamese dialogue
    "image_path": str,              # Full path to image file
    "image_filename": str           # Image filename only
}
```

### Project Info

```python
{
    "project_name": str,            # Project name
    "project_dir": str,             # Full path to project directory
    "output_dir": str,              # Full path to output directory
    "images_dir": str,              # Full path to images directory
    "scripts_dir": str,             # Full path to scripts directory
    "logs_dir": str                 # Full path to logs directory
}
```

---

## Command-Line Interface

### Main Script

```bash
python main.py [OPTIONS]
```

**Options:**
```
--audio AUDIO              Path to input MP3 file (required)
--project PROJECT          Project name (required)
--api-key API_KEY          Gemini API key (optional, can use env var)
--verbose                  Enable verbose logging
-h, --help                 Show help message
```

**Examples:**
```bash
# Basic usage
python main.py --audio story.mp3 --project my_story

# With API key
python main.py --audio story.mp3 --project my_story --api-key YOUR_KEY

# Verbose mode
python main.py --audio story.mp3 --project my_story --verbose
```

---

## Environment Variables

### `GEMINI_API_KEY`

Gemini API key for authentication.

**Usage:**
```bash
export GEMINI_API_KEY=your_api_key_here
python main.py --audio story.mp3 --project my_story
```

---

## Error Handling

### Common Exceptions

#### `FileNotFoundError`
- Audio file not found
- Output directory doesn't exist

#### `ValueError`
- Invalid audio format
- Invalid JSON response
- Invalid configuration

#### `RuntimeError`
- FFmpeg execution failed
- API call failed
- Video creation failed

### Error Handling Example

```python
from main import StoryVideoGenerator

try:
    generator = StoryVideoGenerator("my_story", api_key)
    video_path = generator.run("story.mp3")
except FileNotFoundError as e:
    print(f"File error: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Logging

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about progress
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Accessing Logs

```bash
# View logs
cat projects/my_story/logs/pipeline.log

# Follow logs in real-time
tail -f projects/my_story/logs/pipeline.log
```

### Custom Logging

```python
from utils.logger import setup_logger

logger = setup_logger(__name__, "my_app.log")
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## Performance Metrics

### Typical Execution Times

| Step | Duration | Notes |
|------|----------|-------|
| Audio Analysis | 1-2 min | Depends on audio length |
| Image Generation | 2-5 min | Per image, depends on quality |
| Video Creation | 1-2 min | Depends on number of images |
| **Total** | **5-10 min** | For 3-5 minute audio |

### Memory Usage

| Component | Memory |
|-----------|--------|
| Audio Analysis | 50-100 MB |
| Image Generation | 200-500 MB per image |
| Video Creation | 100-200 MB |
| **Total** | **500 MB - 2 GB** |

---

## Best Practices

1. **API Key Security**
   - Never hardcode API keys
   - Use environment variables
   - Rotate keys regularly

2. **Error Handling**
   - Always wrap API calls in try-except
   - Log errors for debugging
   - Provide user-friendly error messages

3. **Performance**
   - Use shorter audio files for testing
   - Monitor API quotas
   - Cache results when possible

4. **Code Organization**
   - Keep modules focused
   - Use type hints
   - Document complex logic

---

## Examples

### Example 1: Basic Usage

```python
from main import StoryVideoGenerator

generator = StoryVideoGenerator("my_story", "AIzaSyD...")
video = generator.run("story.mp3")
print(f"Video created: {video}")
```

### Example 2: Step-by-Step Processing

```python
from step1_audio_analysis import AudioAnalyzer
from step2_image_generation import ImageGenerator
from step3_video_creation import VideoCreator
from utils.config import Config

config = Config("my_story")
config.setup_directories()

# Step 1
analyzer = AudioAnalyzer("AIzaSyD...")
scripts = analyzer.analyze("story.mp3")

# Step 2
generator = ImageGenerator("AIzaSyD...")
images = generator.generate(scripts, str(config.images_dir))

# Step 3
creator = VideoCreator()
video = creator.create(
    "story.mp3", scripts, images,
    str(config.output_dir), "my_story"
)
```

### Example 3: Error Handling

```python
from main import StoryVideoGenerator

try:
    gen = StoryVideoGenerator("my_story", api_key)
    video = gen.run("story.mp3")
except FileNotFoundError:
    print("Audio file not found")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Support

For issues and questions:
1. Check logs: `projects/your_project/logs/pipeline.log`
2. Enable verbose mode: `--verbose`
3. Review error messages
4. Check README.md and INSTALLATION.md

---

**API Reference Complete! 🚀**

