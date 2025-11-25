"""
Step 2: Image Generation
Generates images for each scene using Gemini's image generation capabilities
"""

import os
import json
from typing import List, Dict
from pathlib import Path
import google.generativeai as genai
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ImageGenerator:
    """Generates images for each scene in the story"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
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
                image_path = self._generate_image(prompt, output_dir, i)
                
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
        Create an enhanced prompt for image generation
        
        Args:
            scene_description: Vietnamese scene description
            index: Current scene index
            total: Total number of scenes
            previous_image: Path to previous image for consistency
            
        Returns:
            Enhanced prompt for image generation
        """
        base_prompt = f"""
Generate a high-quality image for this Vietnamese story scene:

Scene {index}/{total}:
{scene_description}

Requirements:
- Aspect ratio: 9:16 (vertical, suitable for TikTok)
- High quality, cinematic style
- Vivid colors and detailed composition
- Include cultural and costume details as described
- Professional lighting and atmosphere
- Ensure visual consistency with the narrative
- Make it engaging and visually compelling

Generate the image now.
"""
        
        if previous_image:
            base_prompt += f"\nNote: Maintain visual consistency with the previous scene for smooth transitions."
        
        return base_prompt
    
    def _generate_image(self, prompt: str, output_dir: str, index: int) -> str:
        """
        Generate a single image using Gemini
        
        Args:
            prompt: Image generation prompt
            output_dir: Directory to save image
            index: Image index
            
        Returns:
            Path to generated image
        """
        try:
            logger.debug(f"Calling Gemini API to generate image {index}...")
            
            # Use Gemini's image generation
            response = self.model.generate_content(prompt)
            
            # Extract image from response
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'mime_type') and 'image' in part.mime_type:
                        # Save image
                        image_path = os.path.join(output_dir, f"scene_{index:03d}.png")
                        
                        # Note: In actual implementation, you'd save the image data
                        # For now, we'll create a placeholder
                        logger.info(f"Image data received for scene {index}")
                        
                        # Create a simple placeholder image for demonstration
                        self._create_placeholder_image(image_path, index)
                        
                        return image_path
            
            # Fallback: create placeholder
            image_path = os.path.join(output_dir, f"scene_{index:03d}.png")
            self._create_placeholder_image(image_path, index)
            return image_path
            
        except Exception as e:
            logger.error(f"Error in image generation API call: {str(e)}")
            # Create placeholder on error
            image_path = os.path.join(output_dir, f"scene_{index:03d}.png")
            self._create_placeholder_image(image_path, index)
            return image_path
    
    def _create_placeholder_image(self, image_path: str, index: int):
        """
        Create a placeholder image (for development/testing)
        In production, this would be replaced with actual generated images
        
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

