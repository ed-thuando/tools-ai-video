"""
Step 3: Video Creation
Combines images and audio into a final video
"""

import os
import subprocess
from typing import List, Dict
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)


class VideoCreator:
    """Creates final video by combining images and audio"""
    
    def __init__(self):
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
            logger.info("✓ FFmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg not found. Install it with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
    
    def create(self, audio_path: str, scripts_data: List[Dict], images_data: List[Dict], 
               output_dir: str, project_name: str) -> str:
        """
        Create final video by combining images and audio
        
        Args:
            audio_path: Path to input audio file
            scripts_data: List of script segments
            images_data: List of image metadata
            output_dir: Directory to save output video
            project_name: Name of the project
            
        Returns:
            Path to generated video file
        """
        logger.info("Starting video creation process...")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create FFmpeg concat file
        concat_file = self._create_concat_file(images_data, output_dir)
        
        # Create video with audio
        video_path = os.path.join(output_dir, f"{project_name}_final.mp4")
        
        try:
            self._create_video_with_ffmpeg(
                concat_file=concat_file,
                audio_path=audio_path,
                output_path=video_path,
                images_data=images_data
            )
            
            logger.info(f"✓ Video created successfully: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            raise
    
    def _create_concat_file(self, images_data: List[Dict], output_dir: str) -> str:
        """
        Create FFmpeg concat demuxer file
        
        Args:
            images_data: List of image metadata
            output_dir: Directory to save concat file
            
        Returns:
            Path to concat file
        """
        concat_file = os.path.join(output_dir, "concat.txt")
        
        logger.info(f"Creating concat file: {concat_file}")
        
        with open(concat_file, 'w') as f:
            for image in images_data:
                duration = image['duration']
                image_path = image['image_path']
                
                # Write concat format
                f.write(f"file '{image_path}'\n")
                f.write(f"duration {duration}\n")
        
        logger.debug(f"Concat file created with {len(images_data)} entries")
        return concat_file
    
    def _create_video_with_ffmpeg(self, concat_file: str, audio_path: str, 
                                   output_path: str, images_data: List[Dict]):
        """
        Create video using FFmpeg
        
        Args:
            concat_file: Path to FFmpeg concat file
            audio_path: Path to audio file
            output_path: Path to output video
            images_data: List of image metadata
        """
        logger.info("Running FFmpeg to create video...")
        
        # FFmpeg command
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-y",
            output_path
        ]
        
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            
            logger.info("✓ FFmpeg video creation completed")
            
            # Verify output file
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Output file size: {file_size / (1024*1024):.2f} MB")
            else:
                raise FileNotFoundError(f"Output video file not created: {output_path}")
                
        except Exception as e:
            logger.error(f"Error running FFmpeg: {str(e)}")
            raise
    
    def _create_video_with_imageio(self, images_data: List[Dict], audio_path: str, 
                                    output_path: str):
        """
        Alternative method using imageio (fallback if FFmpeg not available)
        
        Args:
            images_data: List of image metadata
            audio_path: Path to audio file
            output_path: Path to output video
        """
        try:
            import imageio
            import numpy as np
            from PIL import Image
            
            logger.info("Using imageio for video creation (FFmpeg not available)")
            
            # Read images
            frames = []
            for image_data in images_data:
                img = Image.open(image_data['image_path'])
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                frames.append(np.array(img))
            
            # Create video writer
            writer = imageio.get_writer(output_path, fps=30)
            
            for i, (frame, image_data) in enumerate(zip(frames, images_data)):
                duration = image_data['duration']
                # Repeat frame for duration
                num_frames = int(duration * 30)  # 30 fps
                for _ in range(num_frames):
                    writer.append_data(frame)
            
            writer.close()
            logger.info(f"✓ Video created with imageio: {output_path}")
            
        except ImportError:
            logger.error("imageio not installed. Please install FFmpeg or imageio.")
            raise

