"""
Step 2: Image Generation
Generates images for each scene using Gemini's image generation capabilities
"""

import os
import json
import time
from typing import List, Dict
from pathlib import Path
from google import genai
from google.genai import types
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ImageGenerator:
    """Generates images for each scene in the story"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.image_model = "gemini-2.5-flash-image"
    
    def generate(self, scripts_data: List[Dict], output_dir: str) -> List[Dict]:
        """
        Generate images for each scene
        
        Args:
            scripts_data: List of script segments with scene descriptions
            output_dir: Directory to save generated images
            
        Returns:
            List of image metadata with paths
        """
        logger.info(f"Starting image generation for {len(scripts_data)} scenes")
        os.makedirs(output_dir, exist_ok=True)
        
        images_data = []
        previous_image_path = None
        
        for i, script in enumerate(scripts_data, 1):
            try:
                logger.info(f"Generating image {i}/{len(scripts_data)}: {script['from']:.2f}s - {script['to']:.2f}s")
                
                # Create enhanced prompt for image generation
                prompt = self._create_image_prompt(
                    script["scene"],
                    i,
                    len(scripts_data),
                    previous_image_path
                )
                
                # Generate image using Gemini
                image_path = self._generate_image(
                    prompt=prompt,
                    scene_description=script["scene"],
                    output_dir=output_dir,
                    index=i
                )
                
                # Store metadata
                image_data = {
                    "index": i,
                    "from": script["from"],
                    "to": script["to"],
                    "duration": script["duration"],
                    "scene_description": script["scene"],
                    "script": script["script"],
                    "image_path": image_path,
                    "image_filename": os.path.basename(image_path)
                }
                
                images_data.append(image_data)
                previous_image_path = image_path
                
                logger.info(f"✓ Image {i} generated: {image_path}")
                
            except Exception as e:
                logger.error(f"Error generating image {i}: {str(e)}")
                raise
        
        logger.info(f"✓ Successfully generated {len(images_data)} images")
        return images_data
    
    def _create_image_prompt(self, scene_description: str, index: int, total: int, previous_image: str = None) -> str:
        """
        Create an enhanced prompt for image generation with Gemini
        
        Args:
            scene_description: Vietnamese scene description
            index: Current scene index
            total: Total number of scenes
            previous_image: Path to previous image for consistency
            
        Returns:
            Enhanced prompt for image generation
        """
        base_prompt = f"""Create a professional, cinematic image for this Vietnamese story scene.

Scene {index} of {total}:
{scene_description}

IMPORTANT REQUIREMENTS:
✓ Vertical aspect ratio: 9:16 (540x960 pixels)
✓ Cinematic quality with professional lighting
✓ Vivid, saturated colors
✓ Detailed composition with depth
✓ Include cultural and costume details as described
✓ Professional atmosphere and mood
✓ Visually compelling and engaging
✓ High resolution, sharp details
✓ Suitable for TikTok vertical video

STYLE: Cinematic, professional, high-quality digital art

Generate the image now. Return ONLY the image, no text or explanation."""
        
        if previous_image:
            base_prompt += f"\n\nNote: Maintain visual consistency with the previous scene for smooth transitions."
        
        return base_prompt
    
    def _generate_image(self, prompt: str, scene_description: str, output_dir: str, index: int) -> str:
        """
        Generate a single image using Gemini
        
        Args:
            prompt: Image generation prompt
            output_dir: Directory to save image
            index: Image index
            
        Returns:
            Path to generated image
        """
        retries = 3
        delay_seconds = 2
        image_path = os.path.join(output_dir, f"scene_{index:03d}.png")
        
        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"Calling Gemini image API (attempt {attempt}/{retries}) to generate image {index}...")
                
                response = self.client.models.generate_content(
                    model=self.image_model,
                    contents=[prompt],
                )
                
                if self._save_image_from_response(response, image_path):
                    logger.info("Image saved from Gemini image API response")
                    return image_path
                
                logger.warning("Gemini response did not include an image. Retrying...")
                time.sleep(delay_seconds)
            except Exception as e:
                logger.error(f"Error in image generation API call: {str(e)}")
                time.sleep(delay_seconds)
        
        logger.warning("No image generated from API after retries, creating enhanced placeholder")
        self._create_enhanced_placeholder_image(image_path, index, scene_description)
        return image_path
    
    def _create_placeholder_image(self, image_path: str, index: int):
        """
        Create a simple placeholder image (for development/testing)
        
        Args:
            image_path: Path to save placeholder image
            index: Image index
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create 9:16 aspect ratio image (540x960 pixels)
            width, height = 540, 960
            img = Image.new('RGB', (width, height), color=(30, 30, 30))
            draw = ImageDraw.Draw(img)
            
            # Add text
            text = f"Scene {index}\n(Generated Image)"
            
            # Try to use a default font, fallback to default
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=(200, 200, 200), font=font)
            
            img.save(image_path)
            logger.debug(f"Placeholder image created: {image_path}")
            
        except ImportError:
            logger.warning("PIL not installed. Creating empty placeholder file.")
            Path(image_path).touch()
        except Exception as e:
            logger.warning(f"Could not create placeholder image: {e}")
            Path(image_path).touch()
    
    def _create_enhanced_placeholder_image(self, image_path: str, index: int, scene_description: str):
        """
        Create an enhanced placeholder image with scene description
        Used when Gemini image generation is not available
        
        Args:
            image_path: Path to save placeholder image
            index: Image index
            scene_description: Scene description from the script
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Create 9:16 aspect ratio image (540x960 pixels)
            width, height = 540, 960
            
            # Create gradient background
            img = Image.new('RGB', (width, height), color=(20, 20, 40))
            draw = ImageDraw.Draw(img)
            
            # Add gradient effect (simple version)
            for y in range(height):
                color_value = int(20 + (y / height) * 60)
                draw.line([(0, y), (width, y)], fill=(color_value, color_value, color_value + 40))
            
            # Add scene number
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
                text_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Draw scene number
            scene_text = f"Scene {index}"
            bbox = draw.textbbox((0, 0), scene_text, font=title_font)
            scene_width = bbox[2] - bbox[0]
            draw.text(((width - scene_width) // 2, 100), scene_text, fill=(100, 200, 255), font=title_font)
            
            # Wrap and draw scene description
            wrapped_text = textwrap.fill(scene_description[:200], width=40)
            lines = wrapped_text.split('\n')
            
            y_offset = 250
            for line in lines[:8]:  # Limit to 8 lines
                bbox = draw.textbbox((0, 0), line, font=text_font)
                line_width = bbox[2] - bbox[0]
                draw.text(((width - line_width) // 2, y_offset), line, fill=(200, 200, 200), font=text_font)
                y_offset += 40
            
            # Add footer
            footer_text = "(Placeholder - Waiting for Gemini image generation)"
            bbox = draw.textbbox((0, 0), footer_text, font=text_font)
            footer_width = bbox[2] - bbox[0]
            draw.text(((width - footer_width) // 2, height - 80), footer_text, fill=(150, 150, 150), font=text_font)
            
            img.save(image_path)
            logger.debug(f"Enhanced placeholder image created: {image_path}")
            
        except Exception as e:
            logger.warning(f"Could not create enhanced placeholder: {e}")
            # Fallback to simple placeholder
            self._create_placeholder_image(image_path, index)

    def _save_image_from_response(self, response, image_path: str) -> bool:
        """
        Inspect Gemini response parts and save the first image found
        """
        if not response or not getattr(response, "parts", None):
            return False
        
        for part in response.parts:
            inline_data = getattr(part, "inline_data", None)
            if inline_data and inline_data.mime_type.startswith("image/"):
                with open(image_path, "wb") as f:
                    f.write(inline_data.data)
                return True
            
            # Some SDK versions expose helper to convert to PIL Image
            if hasattr(part, "as_image"):
                try:
                    image = part.as_image()
                    if image:
                        image.save(image_path, format="PNG")
                        return True
                except Exception as e:
                    logger.debug(f"Failed to convert Gemini part to image: {e}")
            
            text_content = getattr(part, "text", None)
            if text_content:
                logger.debug(f"Gemini text response: {text_content[:100]}")
        
        return False

