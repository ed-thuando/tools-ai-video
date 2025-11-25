#!/usr/bin/env python3
"""
Example usage of the Vietnamese Story Video Generator
Shows how to use the library programmatically
"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from main import StoryVideoGenerator
from utils.logger import setup_logger

logger = setup_logger(__name__)


def example_1_basic_usage():
    """Example 1: Basic usage with command-line style"""
    print("\n" + "="*60)
    print("Example 1: Basic Usage")
    print("="*60)
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    # Create generator
    generator = StoryVideoGenerator(
        project_name="example_story",
        api_key=api_key
    )
    
    # Run with sample audio (you need to provide this)
    audio_path = "sample_story.mp3"
    
    if not os.path.exists(audio_path):
        print(f"Note: Audio file '{audio_path}' not found")
        print("Please provide a valid MP3 file")
        return
    
    try:
        video_path = generator.run(audio_path)
        print(f"\n✓ Video created: {video_path}")
    except Exception as e:
        print(f"Error: {e}")


def example_2_programmatic_usage():
    """Example 2: Programmatic usage with custom settings"""
    print("\n" + "="*60)
    print("Example 2: Programmatic Usage")
    print("="*60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    from step1_audio_analysis import AudioAnalyzer
    from step2_image_generation import ImageGenerator
    from step3_video_creation import VideoCreator
    from utils.config import Config
    
    # Initialize components
    config = Config("custom_project")
    config.setup_directories()
    
    audio_analyzer = AudioAnalyzer(api_key)
    image_generator = ImageGenerator(api_key)
    video_creator = VideoCreator()
    
    audio_path = "sample_story.mp3"
    
    if not os.path.exists(audio_path):
        print(f"Note: Audio file '{audio_path}' not found")
        return
    
    try:
        # Step 1: Analyze audio
        print("\nStep 1: Analyzing audio...")
        scripts_data = audio_analyzer.analyze(audio_path)
        print(f"Generated {len(scripts_data)} script segments")
        
        # Step 2: Generate images
        print("\nStep 2: Generating images...")
        images_data = image_generator.generate(scripts_data, str(config.images_dir))
        print(f"Generated {len(images_data)} images")
        
        # Step 3: Create video
        print("\nStep 3: Creating video...")
        video_path = video_creator.create(
            audio_path=audio_path,
            scripts_data=scripts_data,
            images_data=images_data,
            output_dir=str(config.output_dir),
            project_name="custom_project"
        )
        print(f"✓ Video created: {video_path}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_3_batch_processing():
    """Example 3: Batch processing multiple audio files"""
    print("\n" + "="*60)
    print("Example 3: Batch Processing")
    print("="*60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    # List of audio files to process
    audio_files = [
        "story1.mp3",
        "story2.mp3",
        "story3.mp3",
    ]
    
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        if not os.path.exists(audio_file):
            print(f"Skipping {audio_file} (not found)")
            continue
        
        print(f"\nProcessing {i}/{len(audio_files)}: {audio_file}")
        
        try:
            project_name = Path(audio_file).stem
            generator = StoryVideoGenerator(project_name, api_key)
            video_path = generator.run(audio_file)
            results.append({
                "audio": audio_file,
                "video": video_path,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "audio": audio_file,
                "error": str(e),
                "status": "failed"
            })
    
    # Print summary
    print("\n" + "="*60)
    print("Batch Processing Summary")
    print("="*60)
    for result in results:
        if result["status"] == "success":
            print(f"✓ {result['audio']} -> {result['video']}")
        else:
            print(f"✗ {result['audio']}: {result['error']}")


def example_4_custom_configuration():
    """Example 4: Using custom configuration"""
    print("\n" + "="*60)
    print("Example 4: Custom Configuration")
    print("="*60)
    
    import yaml
    
    # Load custom config
    config_file = "config.yaml"
    if not os.path.exists(config_file):
        print(f"Config file '{config_file}' not found")
        return
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    print("Loaded configuration:")
    print(f"  Image resolution: {config['image']['width']}x{config['image']['height']}")
    print(f"  Video FPS: {config['video']['fps']}")
    print(f"  Video codec: {config['video']['codec']}")
    print(f"  Logging level: {config['logging']['level']}")


def main():
    """Run examples"""
    print("\n" + "="*60)
    print("Vietnamese Story Video Generator - Examples")
    print("="*60)
    
    print("\nAvailable examples:")
    print("1. Basic usage")
    print("2. Programmatic usage")
    print("3. Batch processing")
    print("4. Custom configuration")
    print("0. Exit")
    
    choice = input("\nSelect example (0-4): ").strip()
    
    if choice == "1":
        example_1_basic_usage()
    elif choice == "2":
        example_2_programmatic_usage()
    elif choice == "3":
        example_3_batch_processing()
    elif choice == "4":
        example_4_custom_configuration()
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()

