"""
Step 1: Audio Analysis and Script Generation
Converts MP3 audio to timestamped scripts and scene descriptions
"""

import json
import os
import base64
from typing import List, Dict, Optional
import google.generativeai as genai
from utils.logger import setup_logger

logger = setup_logger(__name__)


DEFAULT_AUDIO_MODEL = os.getenv("GEMINI_AUDIO_MODEL", "gemini-3-pro-preview")


class AudioAnalyzer:
    """Analyzes audio and generates timestamped scripts with scene descriptions"""
    
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        genai.configure(api_key=api_key)
        self.model_name = model_name or DEFAULT_AUDIO_MODEL
        self.model = genai.GenerativeModel(self.model_name)
    
    def _encode_audio(self, audio_path: str) -> str:
        """Encode audio file to base64"""
        with open(audio_path, "rb") as audio_file:
            return base64.standard_b64encode(audio_file.read()).decode("utf-8")
    
    def _time_to_seconds(self, time_str: str) -> float:
        """Convert time string (MM:SS or MM:SS.ms) to seconds"""
        parts = time_str.split(":")
        minutes = int(parts[0])
        seconds_parts = parts[1].split(".")
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
        return minutes * 60 + seconds + milliseconds / 1000
    
    def _seconds_to_milliseconds(self, seconds_value: float) -> int:
        """Convert seconds (float) to integer milliseconds"""
        return int(round(seconds_value * 1000))
    
    def analyze(self, audio_path: str) -> List[Dict]:
        """
        Analyze audio and generate timestamped scripts
        
        Args:
            audio_path: Path to MP3 file
            
        Returns:
            List of script entries with timestamps and scene descriptions
        """
        logger.info(f"Analyzing audio file: {audio_path}")
        
        # Encode audio
        audio_data = self._encode_audio(audio_path)
        
        # Create prompt for Gemini
        prompt = """
Analyze this Vietnamese audio story and create a detailed script breakdown.

For each segment of the story, provide:
1. The exact Vietnamese script/dialogue spoken
2. Start time (in format MM:SS.ms or just seconds as decimal)
3. End time (in format MM:SS.ms or just seconds as decimal)
4. Scene description in Vietnamese (what should be shown visually)

Return the response as a valid JSON array with this structure:
[
  {
    "script": "the vietnamese dialogue or narration",
    "from": 0.0,
    "to": 3.23,
    "scene": "detailed scene description in Vietnamese for visual generation"
  },
  ...
]

Important:
- Be precise with timestamps
- Make scene descriptions vivid and detailed for image generation
- Include all dialogue and important narration
- Ensure timestamps are continuous and don't overlap
- Scene descriptions should be in Vietnamese and detailed enough to generate images
- Include cultural and costume details when relevant
- Describe lighting, mood, and atmosphere

Return ONLY the JSON array, no other text.
"""
        
        try:
            logger.info("Sending audio to Gemini API for analysis...")
            
            # Call Gemini API with audio
            response = self.model.generate_content([
                {
                    "mime_type": "audio/mpeg",
                    "data": audio_data,
                },
                prompt
            ])
            
            response_text = response.text.strip()
            logger.debug(f"Raw response: {response_text[:500]}...")
            
            # Parse JSON response
            try:
                # Try to extract JSON if there's extra text
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                scripts_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                raise ValueError("Failed to parse Gemini response as JSON")
            
            # Validate and normalize data
            scripts_data = self._validate_and_normalize(scripts_data)
            
            logger.info(f"Successfully analyzed audio with model '{self.model_name}'. Generated {len(scripts_data)} script segments")
            for i, script in enumerate(scripts_data, 1):
                start_sec = script.get("from_seconds", script["from"] / 1000)
                end_sec = script.get("to_seconds", script["to"] / 1000)
                logger.info(f"  Segment {i}: {start_sec:.2f}s - {end_sec:.2f}s")
            
            return scripts_data
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            raise
    
    def _validate_and_normalize(self, scripts_data: List[Dict]) -> List[Dict]:
        """
        Validate and normalize script data
        
        Args:
            scripts_data: Raw script data from API
            
        Returns:
            Normalized script data
        """
        normalized = []
        
        for i, item in enumerate(scripts_data):
            # Ensure required fields exist
            if not all(key in item for key in ["script", "from", "to", "scene"]):
                logger.warning(f"Skipping item {i}: missing required fields")
                continue
            
            # Convert times to float if they're strings
            from_time = item["from"]
            to_time = item["to"]
            
            if isinstance(from_time, str):
                from_time = self._time_to_seconds(from_time)
            if isinstance(to_time, str):
                to_time = self._time_to_seconds(to_time)
            
            # Ensure from < to
            if from_time >= to_time:
                logger.warning(f"Item {i}: from time >= to time, swapping")
                from_time, to_time = to_time, from_time
            
            from_ms = self._seconds_to_milliseconds(float(from_time))
            to_ms = self._seconds_to_milliseconds(float(to_time))
            
            if from_ms >= to_ms:
                logger.warning(f"Item {i}: from time >= to time after conversion, adjusting end time by +10ms")
                to_ms = from_ms + 10
            
            duration_ms = to_ms - from_ms
            
            normalized.append({
                "script": str(item["script"]),
                "scene": str(item["scene"]),
                "from": from_ms,
                "to": to_ms,
                "duration": duration_ms,
                "from_seconds": from_ms / 1000.0,
                "to_seconds": to_ms / 1000.0,
                "duration_seconds": duration_ms / 1000.0
            })
        
        return normalized

