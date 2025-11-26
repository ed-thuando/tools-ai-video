#!/usr/bin/env python3
"""
Vietnamese Story Audio to Video Generator - Whisper + LLM Scenes (main4)

Flow:
- Step 1 (new): Use local Whisper model to transcribe MP3 -> SRT
               Then use Gemini text model to group subtitles into scenes
               and generate visual prompts.
- Step 2:      Generate images for each scene with Gemini image model.
- Step 3:      Combine images + original audio into final MP4 video.
"""

import os
import sys
import argparse

from step1_whisper_srt import WhisperSRTSceneAnalyzer
from step2_image_generation import ImageGenerator
from step3_video_creation import VideoCreator
from utils.logger import setup_logger
from utils.config import Config

logger = setup_logger(__name__)


class StoryVideoGeneratorV4:
    """Main orchestrator for the Whisper + LLM scene-based video generation pipeline"""

    def __init__(
        self,
        project_name: str,
        api_key: str,
        whisper_model: str = "small",
        max_scene_duration: float = 8.0,
        language: str = "vi",
        text_model: str = "",
        short_prompt: bool = False,
    ):
        self.project_name = project_name
        self.api_key = api_key
        self.config = Config(project_name)
        self.config.setup_directories()

        # Initialize components
        self.audio_analyzer = WhisperSRTSceneAnalyzer(
            api_key=api_key,
            scripts_dir=str(self.config.scripts_dir),
            whisper_model_name=whisper_model,
            max_scene_duration_seconds=max_scene_duration,
            language=language,
            text_model_name=text_model or None,
        )
        # Image generator (now supports optional short prompts + concurrency)
        self.image_generator = ImageGenerator(api_key, short_prompt=short_prompt)
        self.video_creator = VideoCreator()

        logger.info("Initialized StoryVideoGeneratorV4 for project: %s", project_name)
        logger.info("Whisper model: %s", whisper_model)
        logger.info("Max scene duration: %.2fs", max_scene_duration)
        logger.info("Subtitle language hint: %s", language)
        if text_model:
            logger.info("Using custom Gemini text model: %s", text_model)
        else:
            logger.info("Using default Gemini text model from environment or fallback")

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

            if not audio_path.lower().endswith(".mp3"):
                raise ValueError("Input file must be an MP3 file")

            logger.info("=" * 60)
            logger.info("Starting main4 pipeline (Whisper + LLM scenes)")
            logger.info("Audio: %s", audio_path)
            logger.info("=" * 60)

            # Step 1: Whisper -> SRT -> LLM scenes
            logger.info("\n" + "=" * 60)
            logger.info("STEP 1: Transcribing audio with Whisper and generating scenes with LLM...")
            logger.info("=" * 60)
            scripts_data = self.audio_analyzer.analyze(audio_path)
            scripts_file = self.config.save_scripts(scripts_data)
            logger.info("Scene scripts saved to: %s", scripts_file)

            # Step 2: Generate images based on scenes
            logger.info("\n" + "=" * 60)
            logger.info("STEP 2: Generating images for each scene...")
            logger.info("=" * 60)
            images_data = self.image_generator.generate(scripts_data, self.config.images_dir)
            images_file = self.config.save_images_metadata(images_data)
            logger.info("Images metadata saved to: %s", images_file)

            # Step 3: Create final video
            logger.info("\n" + "=" * 60)
            logger.info("STEP 3: Creating final video...")
            logger.info("=" * 60)
            video_path = self.video_creator.create(
                audio_path=audio_path,
                scripts_data=scripts_data,
                images_data=images_data,
                output_dir=self.config.output_dir,
                project_name=self.project_name,
            )

            logger.info("\n" + "=" * 60)
            logger.info("✓ main4 video generation completed successfully!")
            logger.info("Output video: %s", video_path)
            logger.info("=" * 60)

            return video_path

        except Exception as e:
            logger.error("Pipeline failed: %s", str(e), exc_info=True)
            raise


def main():
    """Main entry point for main4 pipeline"""
    parser = argparse.ArgumentParser(
        description=(
            "Vietnamese Story Audio to Video Generator (main4) - "
            "Local Whisper + LLM scene generation"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main4.py --audio story.mp3 --project my_story
  python main4.py --audio tnk.mp3 --project tnk --whisper-model small --max-scene-duration 8
  python main4.py --audio input.mp3 --project demo \\
      --api-key YOUR_API_KEY --whisper-model base --language vi
        """,
    )

    parser.add_argument(
        "--audio",
        required=True,
        help="Path to input MP3 audio file",
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project name (used for output directory under ./projects)",
    )
    parser.add_argument(
        "--api-key",
        help="Gemini API key (or set GEMINI_API_KEY environment variable)",
    )
    parser.add_argument(
        "--whisper-model",
        default="small",
        help="Local Whisper model name (tiny, base, small, medium, large). Default: small",
    )
    parser.add_argument(
        "--max-scene-duration",
        type=float,
        default=8.0,
        help="Maximum scene duration in seconds (default: 8.0)",
    )
    parser.add_argument(
        "--language",
        default="vi",
        help="Language hint for Whisper transcription (e.g. 'vi', 'en'). Default: vi",
    )
    parser.add_argument(
        "--text-model",
        default="",
        help="Override Gemini text model for scene generation (default: GEMINI_TEXT_MODEL env or gemini-2.0-flash-lite)",
    )
    parser.add_argument(
        "--short-prompt",
        action="store_true",
        help="Use shorter image prompts (more concise, similar style to main3)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error(
            "Gemini API key not provided. Set GEMINI_API_KEY environment variable or use --api-key"
        )
        sys.exit(1)

    try:
        generator = StoryVideoGeneratorV4(
            project_name=args.project,
            api_key=api_key,
            whisper_model=args.whisper_model,
            max_scene_duration=args.max_scene_duration,
            language=args.language,
            text_model=args.text_model,
            short_prompt=args.short_prompt,
        )
        video_path = generator.run(args.audio)
        print(f"\n✓ Success! main4 video saved to: {video_path}")
    except Exception as e:
        logger.error("Fatal error in main4: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()


