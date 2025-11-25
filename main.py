#!/usr/bin/env python3
"""
Vietnamese Story Audio to Video Generator
Converts MP3 audio to video with AI-generated scenes and images
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

# Import custom modules
from step1_audio_analysis import AudioAnalyzer
from step2_image_generation import ImageGenerator
from step3_video_creation import VideoCreator
from utils.logger import setup_logger
from utils.config import Config

logger = setup_logger(__name__)


class StoryVideoGenerator:
    """Main orchestrator for the story video generation pipeline"""
    
    def __init__(self, project_name: str, api_key: str):
        self.project_name = project_name
        self.api_key = api_key
        self.config = Config(project_name)
        self.config.setup_directories()
        
        # Initialize components
        self.audio_analyzer = AudioAnalyzer(api_key)
        self.image_generator = ImageGenerator(api_key)
        self.video_creator = VideoCreator()
        
        logger.info(f"Initialized StoryVideoGenerator for project: {project_name}")
    
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
            
            # Step 1: Analyze audio and create scripts with timestamps
            logger.info("=" * 60)
            logger.info("STEP 1: Analyzing audio and generating scripts...")
            logger.info("=" * 60)
            scripts_data = self.audio_analyzer.analyze(audio_path)
            scripts_file = self.config.save_scripts(scripts_data)
            logger.info(f"Scripts saved to: {scripts_file}")
            
            # Step 2: Generate images based on scenes
            logger.info("\n" + "=" * 60)
            logger.info("STEP 2: Generating images for each scene...")
            logger.info("=" * 60)
            images_data = self.image_generator.generate(scripts_data, self.config.images_dir)
            images_file = self.config.save_images_metadata(images_data)
            logger.info(f"Images metadata saved to: {images_file}")
            
            # Step 3: Create final video
            logger.info("\n" + "=" * 60)
            logger.info("STEP 3: Creating final video...")
            logger.info("=" * 60)
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
        description="Vietnamese Story Audio to Video Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --audio story.mp3 --project my_story
  python main.py --audio input.mp3 --project tiktok_video --api-key YOUR_API_KEY
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
        generator = StoryVideoGenerator(args.project, api_key)
        video_path = generator.run(args.audio)
        print(f"\n✓ Success! Video saved to: {video_path}")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

