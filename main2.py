#!/usr/bin/env python3
"""
Vietnamese Story Audio to Video Generator - New Flow
Splits audio into partitions, generates images from audio using Gemini 3 Flash,
then creates video with images and audio
"""

import os
import json
import sys
import base64
import time
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from pydub import AudioSegment

# Import custom modules
from step3_video_creation import VideoCreator
from utils.logger import setup_logger
from utils.config import Config
import google.generativeai as genai
from google import genai as genai_client
from google.genai import types

logger = setup_logger(__name__)


class AudioSplitter:
    """Splits audio into fixed-duration partitions"""
    
    def __init__(self, partition_duration: float = 8.0):
        """
        Initialize audio splitter
        
        Args:
            partition_duration: Duration of each partition in seconds (default: 8.0)
        """
        self.partition_duration = partition_duration
        logger.info(f"Audio splitter initialized with partition duration: {partition_duration}s")
    
    def split(self, audio_path: str, output_dir: str) -> List[Dict]:
        """
        Split audio file into partitions
        
        Args:
            audio_path: Path to input MP3 file
            output_dir: Directory to save audio partitions
            
        Returns:
            List of partition metadata with paths and timestamps
        """
        logger.info(f"Splitting audio file: {audio_path}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Load audio
        audio = AudioSegment.from_mp3(audio_path)
        total_duration_ms = len(audio)
        total_duration_sec = total_duration_ms / 1000.0
        partition_duration_ms = int(self.partition_duration * 1000)
        
        logger.info(f"Total audio duration: {total_duration_sec:.2f}s")
        logger.info(f"Partition duration: {self.partition_duration:.2f}s")
        
        partitions = []
        partition_index = 1
        start_ms = 0
        
        while start_ms < total_duration_ms:
            # Calculate end time
            end_ms = min(start_ms + partition_duration_ms, total_duration_ms)
            actual_duration_ms = end_ms - start_ms
            actual_duration_sec = actual_duration_ms / 1000.0
            
            # Extract partition
            partition_audio = audio[start_ms:end_ms]
            
            # Save partition
            partition_filename = f"partition_{partition_index:03d}.mp3"
            partition_path = os.path.join(output_dir, partition_filename)
            partition_audio.export(partition_path, format="mp3")
            
            # Store metadata
            partition_data = {
                "index": partition_index,
                "start_seconds": start_ms / 1000.0,
                "end_seconds": end_ms / 1000.0,
                "duration_seconds": actual_duration_sec,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "duration_ms": actual_duration_ms,
                "audio_path": partition_path,
                "audio_filename": partition_filename
            }
            
            partitions.append(partition_data)
            logger.info(
                f"Partition {partition_index}: {partition_data['start_seconds']:.2f}s - "
                f"{partition_data['end_seconds']:.2f}s (duration: {actual_duration_sec:.2f}s)"
            )
            
            # Move to next partition
            start_ms = end_ms
            partition_index += 1
        
        logger.info(f"✓ Successfully split audio into {len(partitions)} partitions")
        return partitions


class AudioToImageGenerator:
    """Generates images from audio partitions using Gemini 3 Flash"""
    
    def __init__(self, api_key: str, audio_model_name: Optional[str] = None):
        """
        Initialize audio-to-image generator
        
        Args:
            api_key: Gemini API key
            audio_model_name: Optional override for Gemini audio model
        """
        genai.configure(api_key=api_key)
        self.client = genai_client.Client(api_key=api_key)
        self.audio_model_name = audio_model_name or os.getenv("GEMINI_AUDIO_MODEL", "gemini-2.5-flash")
        self.image_model = "gemini-2.5-flash-image"
        self.audio_model = genai.GenerativeModel(self.audio_model_name)
        
        # Get image aspect ratio from config or env
        image_aspect_ratio = os.getenv("GEMINI_IMAGE_ASPECT_RATIO", "9:16")
        self.image_generation_config = types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio=image_aspect_ratio,
            )
        )
        logger.info(
            "Audio-to-image generator initialized with aspect ratio %s using audio model %s",
            image_aspect_ratio,
            self.audio_model_name,
        )
    
    def _encode_audio(self, audio_path: str) -> str:
        """Encode audio file to base64"""
        with open(audio_path, "rb") as audio_file:
            return base64.standard_b64encode(audio_file.read()).decode("utf-8")
    
    def generate_image_from_audio(self, audio_path: str, partition_index: int, 
                                   total_partitions: int, output_dir: str) -> str:
        """
        Generate an image from an audio partition using Gemini 3 Flash
        
        Args:
            audio_path: Path to audio partition file
            partition_index: Current partition index
            total_partitions: Total number of partitions
            output_dir: Directory to save generated image
            
        Returns:
            Path to generated image
        """
        logger.info(f"Generating image {partition_index}/{total_partitions} from audio...")
        
        # Encode audio
        audio_data = self._encode_audio(audio_path)
        
        # Create prompt for Gemini
        prompt = """
Analyze this audio segment and generate a detailed visual description of what should be shown in an image.

Based on the audio content (speech, music, sounds, tone, mood, etc.), create a vivid, detailed description of a scene that matches the audio.

The description should be:
- Detailed and specific enough for image generation
- Match the mood, tone, and content of the audio
- Include visual elements, colors, lighting, atmosphere
- Suitable for creating a cinematic, professional image
- In Vietnamese if the audio is in Vietnamese, or in English if needed

Return ONLY the visual description text, no JSON, no formatting, just the description.
"""
        
        retries = 3
        delay_seconds = 2
        
        for attempt in range(1, retries + 1):
            try:
                # Step 1: Analyze audio and get scene description
                logger.debug(f"Analyzing audio with Gemini (attempt {attempt}/{retries})...")
                
                response = self.audio_model.generate_content([
                    {
                        "mime_type": "audio/mpeg",
                        "data": audio_data,
                    },
                    prompt
                ])
                
                scene_description = response.text.strip()
                logger.debug(f"Scene description: {scene_description[:200]}...")
                
                # Step 2: Generate image from scene description
                logger.debug(f"Generating image from description (attempt {attempt}/{retries})...")
                
                image_prompt = f"""Create a professional, cinematic image for this scene.

{scene_description}

IMPORTANT REQUIREMENTS:
✓ Vertical aspect ratio: 9:16 (540x960 pixels)
✓ Cinematic quality with professional lighting
✓ Vivid, saturated colors
✓ Detailed composition with depth
✓ Professional atmosphere and mood
✓ Visually compelling and engaging
✓ High resolution, sharp details
✓ Suitable for TikTok vertical video

STYLE: Cinematic, professional, high-quality digital art

Generate the image now. Return ONLY the image, no text or explanation."""
                
                image_response = self.client.models.generate_content(
                    model=self.image_model,
                    contents=[image_prompt],
                    config=self.image_generation_config,
                )
                
                # Save image
                image_path = os.path.join(output_dir, f"scene_{partition_index:03d}.png")
                if self._save_image_from_response(image_response, image_path):
                    logger.info(f"✓ Image {partition_index} generated: {image_path}")
                    return image_path
                
                logger.warning(f"Image generation attempt {attempt} did not return an image. Retrying...")
                time.sleep(delay_seconds)
                
            except Exception as e:
                logger.error(f"Error in image generation (attempt {attempt}): {str(e)}")
                if attempt < retries:
                    time.sleep(delay_seconds)
                else:
                    raise
        
        # Fallback: create placeholder if all retries failed
        logger.warning("All retries failed, creating placeholder image")
        image_path = os.path.join(output_dir, f"scene_{partition_index:03d}.png")
        self._create_placeholder_image(image_path, partition_index)
        return image_path
    
    def _save_image_from_response(self, response, image_path: str) -> bool:
        """Save image from Gemini response"""
        if not response or not getattr(response, "parts", None):
            return False
        
        for part in response.parts:
            inline_data = getattr(part, "inline_data", None)
            if inline_data and inline_data.mime_type.startswith("image/"):
                with open(image_path, "wb") as f:
                    f.write(inline_data.data)
                return True
            
            if hasattr(part, "as_image"):
                try:
                    image = part.as_image()
                    if image:
                        image.save(image_path, format="PNG")
                        return True
                except Exception as e:
                    logger.debug(f"Failed to convert Gemini part to image: {e}")
        
        return False
    
    def _create_placeholder_image(self, image_path: str, index: int):
        """Create a placeholder image if generation fails"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            width, height = 540, 960
            img = Image.new('RGB', (width, height), color=(30, 30, 30))
            draw = ImageDraw.Draw(img)
            
            text = f"Scene {index}\n(Generated Image)"
            
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=(200, 200, 200), font=font)
            img.save(image_path)
            logger.debug(f"Placeholder image created: {image_path}")
            
        except Exception as e:
            logger.warning(f"Could not create placeholder image: {e}")
            Path(image_path).touch()
    
    def generate_all_images(self, partitions: List[Dict], output_dir: str) -> List[Dict]:
        """
        Generate images for all audio partitions
        
        Args:
            partitions: List of partition metadata
            output_dir: Directory to save generated images
            
        Returns:
            List of image metadata with paths
        """
        logger.info(f"Starting image generation for {len(partitions)} partitions")
        os.makedirs(output_dir, exist_ok=True)
        
        images_data = []
        
        for partition in partitions:
            try:
                image_path = self.generate_image_from_audio(
                    audio_path=partition["audio_path"],
                    partition_index=partition["index"],
                    total_partitions=len(partitions),
                    output_dir=output_dir
                )
                
                # Store metadata
                image_data = {
                    "index": partition["index"],
                    "from": partition["start_ms"],
                    "to": partition["end_ms"],
                    "duration": partition["duration_seconds"],
                    "duration_ms": partition["duration_ms"],
                    "from_seconds": partition["start_seconds"],
                    "to_seconds": partition["end_seconds"],
                    "duration_seconds": partition["duration_seconds"],
                    "image_path": image_path,
                    "image_filename": os.path.basename(image_path),
                    "audio_path": partition["audio_path"]
                }
                
                images_data.append(image_data)
                
            except Exception as e:
                logger.error(f"Error generating image for partition {partition['index']}: {str(e)}")
                raise
        
        logger.info(f"✓ Successfully generated {len(images_data)} images")
        return images_data


class StoryVideoGeneratorV2:
    """Main orchestrator for the new story video generation pipeline"""
    
    def __init__(
        self,
        project_name: str,
        api_key: str,
        partition_duration: float = 8.0,
        audio_model_name: Optional[str] = None,
    ):
        """
        Initialize generator
        
        Args:
            project_name: Name of the project
            api_key: Gemini API key
            partition_duration: Duration of each audio partition in seconds (default: 8.0)
            audio_model_name: Optional override for the Gemini audio model
        """
        self.project_name = project_name
        self.api_key = api_key
        self.partition_duration = partition_duration
        self.audio_model_name = audio_model_name
        self.config = Config(project_name)
        self.config.setup_directories()
        
        # Initialize components
        self.audio_splitter = AudioSplitter(partition_duration)
        self.image_generator = AudioToImageGenerator(api_key, audio_model_name=audio_model_name)
        self.video_creator = VideoCreator()
        
        logger.info(f"Initialized StoryVideoGeneratorV2 for project: {project_name}")
        logger.info(f"Partition duration: {partition_duration}s")
        if self.audio_model_name:
            logger.info("Using custom audio model: %s", self.audio_model_name)
        else:
            logger.info("Using default audio model from environment or fallback")
    
    def run(self, audio_path: str) -> str:
        """
        Execute the complete pipeline
        
        Args:
            audio_path: Path to the input MP3 file
            
        Returns:
            Path to the generated video file
        """
        try:
            # Validate input
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            if not audio_path.lower().endswith('.mp3'):
                raise ValueError("Input file must be an MP3 file")
            
            logger.info(f"Starting pipeline with audio: {audio_path}")
            
            # Step 1: Split audio into partitions
            logger.info("=" * 60)
            logger.info("STEP 1: Splitting audio into partitions...")
            logger.info("=" * 60)
            partitions_dir = os.path.join(self.config.project_dir, "partitions")
            partitions = self.audio_splitter.split(audio_path, partitions_dir)
            logger.info(f"✓ Created {len(partitions)} audio partitions")
            
            # Step 2: Generate images from audio partitions
            logger.info("\n" + "=" * 60)
            logger.info("STEP 2: Generating images from audio partitions...")
            logger.info("=" * 60)
            images_data = self.image_generator.generate_all_images(partitions, self.config.images_dir)
            logger.info(f"✓ Generated {len(images_data)} images")
            
            # Step 3: Create final video
            logger.info("\n" + "=" * 60)
            logger.info("STEP 3: Creating final video...")
            logger.info("=" * 60)
            
            # Create dummy scripts_data for video creator (it needs this format)
            scripts_data = []
            for img_data in images_data:
                scripts_data.append({
                    "from": img_data["from"],
                    "to": img_data["to"],
                    "duration": img_data["duration_ms"],
                    "from_seconds": img_data["from_seconds"],
                    "to_seconds": img_data["to_seconds"],
                    "duration_seconds": img_data["duration_seconds"]
                })
            
            video_path = self.video_creator.create(
                audio_path=audio_path,
                scripts_data=scripts_data,
                images_data=images_data,
                output_dir=self.config.output_dir,
                project_name=self.project_name
            )
            
            logger.info("\n" + "=" * 60)
            logger.info(f"✓ Video generation completed successfully!")
            logger.info(f"Output video: {video_path}")
            logger.info("=" * 60)
            
            return video_path
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Vietnamese Story Audio to Video Generator - New Flow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main2.py --audio story.mp3 --project my_story
  python main2.py --audio input.mp3 --project tiktok_video --partition-duration 10
  python main2.py --audio input.mp3 --project my_video --api-key YOUR_API_KEY --partition-duration 8
        """
    )
    
    parser.add_argument(
        "--audio",
        required=True,
        help="Path to input MP3 audio file"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project name (used for output directory)"
    )
    parser.add_argument(
        "--api-key",
        help="Gemini API key (or set GEMINI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--partition-duration",
        type=float,
        default=8.0,
        help="Duration of each audio partition in seconds (default: 8.0)"
    )
    parser.add_argument(
        "--audio-model",
        help="Override Gemini audio model used for scene extraction (default: GEMINI_AUDIO_MODEL env or gemini-2.5-flash)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("Gemini API key not provided. Set GEMINI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    try:
        # Create generator and run pipeline
        generator = StoryVideoGeneratorV2(
            args.project, 
            api_key, 
            partition_duration=args.partition_duration,
            audio_model_name=args.audio_model
        )
        video_path = generator.run(args.audio)
        print(f"\n✓ Success! Video saved to: {video_path}")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

