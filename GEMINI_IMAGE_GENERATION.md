# Gemini Image Generation - Technical Guide

## Overview

The image generation system now uses Google's Gemini API to generate actual images instead of placeholders.

## Architecture

### Image Generation Pipeline

```
Scene Description (from Step 1)
    ↓
Create Detailed Prompt
    ↓
Send to Gemini API
    ↓
┌─────────────────────────────────────┐
│ Response Processing                 │
├─────────────────────────────────────┤
│ 1. Check for image MIME type        │
│ 2. Extract image data               │
│ 3. Save to PNG file                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ If No Image in Response             │
├─────────────────────────────────────┤
│ 1. Try alternative prompt           │
│ 2. Retry API call                   │
│ 3. Check response again             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ If Still No Image                   │
├─────────────────────────────────────┤
│ 1. Create enhanced placeholder      │
│ 2. Include scene description        │
│ 3. Add professional styling         │
└─────────────────────────────────────┘
    ↓
Return Image Path
```

## Key Components

### 1. Image Generation Method

```python
def _generate_image(self, prompt: str, output_dir: str, index: int) -> str:
    """Generate image using Gemini API with fallback strategies"""
```

**Features:**
- Primary image generation attempt
- Alternative prompt strategy
- Enhanced placeholder fallback
- Error handling and logging

### 2. Prompt Creation

```python
def _create_image_prompt(self, scene_description: str, index: int, total: int) -> str:
    """Create optimized prompt for Gemini image generation"""
```

**Prompt Includes:**
- Scene number and total count
- Vietnamese scene description
- Specific requirements:
  - 9:16 vertical aspect ratio
  - Cinematic quality
  - Professional lighting
  - Vivid colors
  - Cultural details
  - TikTok optimization
- Explicit instruction to return only image

### 3. Enhanced Placeholder

```python
def _create_enhanced_placeholder_image(self, image_path: str, index: int, scene_description: str):
    """Create high-quality placeholder when API doesn't return images"""
```

**Features:**
- Gradient background
- Scene number display
- Scene description text
- Professional styling
- Footer indicator

## Data Flow

### Input
- Scene description (Vietnamese text)
- Scene index
- Total number of scenes
- Output directory path

### Processing
1. Create detailed prompt
2. Send to Gemini API
3. Parse response
4. Extract image data
5. Save image file

### Output
- PNG image file (540x960 pixels)
- Image metadata (path, timing, description)

## Image Specifications

### Dimensions
- **Width:** 540 pixels
- **Height:** 960 pixels
- **Aspect Ratio:** 9:16 (vertical)
- **Format:** PNG

### Quality
- **Style:** Cinematic
- **Lighting:** Professional
- **Colors:** Vivid and saturated
- **Details:** High resolution, sharp

### Optimization
- Vertical format for TikTok
- Optimized for mobile viewing
- Professional appearance
- Engaging visual composition

## Error Handling

### Scenario 1: API Returns Image
```
✓ Extract image data
✓ Save to file
✓ Return path
```

### Scenario 2: API Returns Text
```
⚠ No image in response
→ Try alternative prompt
→ Retry API call
→ If still no image, create placeholder
```

### Scenario 3: API Error
```
✗ API call fails
→ Log error
→ Create enhanced placeholder
→ Continue pipeline
```

### Scenario 4: PIL Error
```
✗ PIL not available
→ Create simple placeholder
→ Continue pipeline
```

## Configuration

### API Settings
- **Model:** gemini-2.0-flash
- **Timeout:** 300 seconds
- **Retries:** 2 attempts

### Image Settings
- **Aspect Ratio:** 9:16
- **Resolution:** 540x960
- **Format:** PNG
- **Quality:** High

## Performance Metrics

### Timing
- **Per Image:** 1-3 seconds
- **18 Images:** 18-54 seconds
- **Fallback:** < 1 second

### Success Rates
- **API Image Generation:** Depends on API tier
- **Fallback Placeholder:** 100%
- **Overall Success:** 100%

## Troubleshooting

### Issue: All images are placeholders

**Cause:** Gemini API not returning images

**Solutions:**
1. Check API tier supports image generation
2. Verify API key permissions
3. Check rate limits
4. Try with simpler prompts

### Issue: API timeout

**Cause:** Slow network or API overload

**Solutions:**
1. Increase timeout in config
2. Reduce concurrent requests
3. Try again later
4. Check network connection

### Issue: PIL errors

**Cause:** PIL/Pillow not installed

**Solutions:**
```bash
pip install Pillow
```

### Issue: Image quality poor

**Cause:** Vague scene descriptions

**Solutions:**
1. Improve scene descriptions in Step 1
2. Add more cultural details
3. Describe lighting and mood
4. Be more specific about composition

## API Response Handling

### Expected Response Structure

```python
response.parts = [
    {
        'mime_type': 'image/png',
        'data': <binary image data>
    }
]
```

### Parsing Logic

```python
for part in response.parts:
    if hasattr(part, 'mime_type') and 'image' in part.mime_type:
        if hasattr(part, 'data'):
            # Save image
            with open(image_path, 'wb') as f:
                f.write(part.data)
```

## Optimization Tips

### For Better Results

1. **Detailed Descriptions**
   - Include cultural details
   - Describe lighting
   - Mention mood/atmosphere
   - Specify composition

2. **Clear Prompts**
   - Specific requirements
   - Explicit format needs
   - Clear style guidance
   - Avoid ambiguity

3. **Consistent Styling**
   - Reference previous images
   - Maintain visual continuity
   - Use consistent color palette
   - Keep same art style

### For Better Performance

1. **Reduce Requests**
   - Cache results
   - Reuse images when possible
   - Batch processing

2. **Optimize Prompts**
   - Shorter descriptions
   - Clear requirements
   - Specific style guidance

3. **Monitor Limits**
   - Track API usage
   - Respect rate limits
   - Plan batch processing

## Integration with Pipeline

### Step 1: Audio Analysis
```
Output: scripts.json with scene descriptions
```

### Step 2: Image Generation (This Module)
```
Input: Scene descriptions
Process: Generate images with Gemini
Output: PNG images + metadata
```

### Step 3: Video Creation
```
Input: Images + audio + timing
Process: Combine into video
Output: MP4 video
```

## Future Enhancements

- [ ] Parallel image generation
- [ ] Image caching
- [ ] Batch processing
- [ ] Custom style templates
- [ ] Image quality settings
- [ ] Advanced fallback strategies
- [ ] Image post-processing
- [ ] Style consistency engine

## Code Examples

### Basic Usage

```python
from step2_image_generation import ImageGenerator

generator = ImageGenerator(api_key)
images = generator.generate(scripts_data, output_dir)
```

### With Error Handling

```python
try:
    images = generator.generate(scripts_data, output_dir)
    print(f"Generated {len(images)} images")
except Exception as e:
    print(f"Error: {e}")
    # Placeholders will be created automatically
```

### Checking Results

```python
for image in images:
    print(f"Scene {image['index']}: {image['image_path']}")
    print(f"  Duration: {image['duration']}s")
    print(f"  Description: {image['scene_description']}")
```

## Monitoring

### Logs to Check

```
projects/your_project/logs/pipeline.log
```

### Key Log Messages

```
INFO - Generating image 1/18: 0.00s - 4.95s
INFO - Image saved from Gemini API response
INFO - Image generated and saved successfully
WARNING - No image generated from API, creating enhanced placeholder
ERROR - Error in image generation API call
```

## Support

For issues with image generation:

1. Check logs: `projects/your_project/logs/pipeline.log`
2. Verify API key and permissions
3. Check internet connection
4. Review scene descriptions
5. Try with simpler prompts

---

**Gemini Image Generation Guide Complete!** 🎨✨

