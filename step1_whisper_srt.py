"""
Step 1 (alt): Local Whisper + LLM Scene Generation

Flow:
- Use local Whisper model to transcribe MP3 -> SRT file
- Feed SRT (or plain text version) into Gemini text model
- Ask Gemini to group subtitles into visual scenes (< ~8 seconds) and
  generate a visual prompt for each scene
- Normalize output into the same `scripts_data` structure used by the
  rest of the pipeline.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

import google.generativeai as genai

from utils.logger import setup_logger

logger = setup_logger(__name__)


DEFAULT_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.0-flash-lite")


@dataclass
class SubtitleSegment:
    index: int
    start_ms: int
    end_ms: int
    text: str

    @property
    def duration_ms(self) -> int:
        return max(0, self.end_ms - self.start_ms)


class WhisperSRTSceneAnalyzer:
    """
    Analyze audio using local Whisper, then use LLM to convert subtitles
    into timestamped scenes compatible with the rest of the pipeline.
    """

    def __init__(
        self,
        api_key: str,
        scripts_dir: str,
        whisper_model_name: str = "small",
        max_scene_duration_seconds: float = 8.0,
        language: Optional[str] = "vi",
        text_model_name: Optional[str] = None,
    ):
        """
        Args:
            api_key: Gemini API key (for scene generation, not transcription)
            scripts_dir: Where to save SRT and intermediate files
            whisper_model_name: Local Whisper model name (e.g. tiny, base, small, medium, large)
            max_scene_duration_seconds: Maximum duration of one scene in seconds
            language: Hint language code for Whisper (e.g. 'vi' for Vietnamese)
            text_model_name: Optional override for Gemini text model
        """
        # LLM config
        genai.configure(api_key=api_key)
        self.text_model_name = text_model_name or DEFAULT_TEXT_MODEL
        self.text_model = genai.GenerativeModel(self.text_model_name)

        # Whisper config (lazy-loaded)
        self.whisper_model_name = whisper_model_name
        self.language = language
        self.max_scene_duration_seconds = max_scene_duration_seconds

        # Paths
        self.scripts_dir = Path(scripts_dir)
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.srt_path = self.scripts_dir / "subtitles_whisper.srt"
        self.raw_subtitles_json = self.scripts_dir / "subtitles_whisper.json"

        logger.info(
            "WhisperSRTSceneAnalyzer initialized (whisper=%s, text model=%s, max_scene_duration=%.2fs)",
            self.whisper_model_name,
            self.text_model_name,
            self.max_scene_duration_seconds,
        )

    # ---------- Public API ----------

    def analyze(self, audio_path: str) -> List[Dict]:
        """
        End-to-end analysis:
        - audio.mp3 -> Whisper -> SRT
        - SRT -> subtitles list
        - subtitles list -> Gemini -> scene list
        - normalize to scripts_data
        """
        logger.info("Analyzing audio with local Whisper + LLM scenes: %s", audio_path)

        # 1) Transcribe with Whisper (local)
        subtitle_segments = self._transcribe_with_whisper(audio_path)

        # 2) Persist raw subtitles (SRT + JSON) for debugging / inspection
        self._save_srt(subtitle_segments, self.srt_path)
        self._save_raw_subtitles_json(subtitle_segments, self.raw_subtitles_json)

        # 3) Ask Gemini to group subtitles into visual scenes
        scripts_data_raw = self._generate_scenes_with_llm(subtitle_segments)

        # 4) Normalize to canonical `scripts_data` structure
        scripts_data = self._validate_and_normalize(scripts_data_raw)

        logger.info("Generated %d scenes from Whisper+LLM", len(scripts_data))
        for i, script in enumerate(scripts_data, 1):
            logger.info(
                "  Scene %d: %.2fs -> %.2fs (%.2fs)",
                i,
                script["from_seconds"],
                script["to_seconds"],
                script["duration_seconds"],
            )

        return scripts_data

    # ---------- Whisper ----------

    def _load_whisper_model(self):
        try:
            import whisper  # type: ignore
        except ImportError as e:
            logger.error(
                "The 'whisper' package is required. Install with: pip install openai-whisper"
            )
            raise e

        logger.info("Loading Whisper model: %s (this may take a moment)", self.whisper_model_name)
        model = whisper.load_model(self.whisper_model_name)
        return model

    def _transcribe_with_whisper(self, audio_path: str) -> List[SubtitleSegment]:
        model = self._load_whisper_model()

        logger.info("Transcribing audio with Whisper: %s", audio_path)
        result = model.transcribe(
            audio_path,
            task="transcribe",
            language=self.language,
            verbose=False,
        )

        segments: List[SubtitleSegment] = []
        for seg in result.get("segments", []):
            index = int(seg.get("id", len(segments))) + 1
            start_ms = int(round(float(seg["start"]) * 1000))
            end_ms = int(round(float(seg["end"]) * 1000))
            text = str(seg.get("text", "")).strip()
            if not text:
                continue
            segments.append(SubtitleSegment(index=index, start_ms=start_ms, end_ms=end_ms, text=text))

        if not segments:
            raise ValueError("Whisper did not return any subtitle segments")

        logger.info("Whisper produced %d subtitle segments", len(segments))
        return segments

    # ---------- SRT helpers ----------

    @staticmethod
    def _format_srt_timestamp(ms: int) -> str:
        total_seconds = ms // 1000
        milliseconds = ms % 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def _save_srt(self, segments: List[SubtitleSegment], path: Path) -> None:
        logger.info("Saving Whisper subtitles to SRT: %s", path)
        lines = []
        for seg in segments:
            start_ts = self._format_srt_timestamp(seg.start_ms)
            end_ts = self._format_srt_timestamp(seg.end_ms)
            lines.append(str(seg.index))
            lines.append(f"{start_ts} --> {end_ts}")
            lines.append(seg.text)
            lines.append("")  # blank line between entries
        path.write_text("\n".join(lines), encoding="utf-8")

    def _save_raw_subtitles_json(self, segments: List[SubtitleSegment], path: Path) -> None:
        data = [
            {
                "index": seg.index,
                "start_ms": seg.start_ms,
                "end_ms": seg.end_ms,
                "duration_ms": seg.duration_ms,
                "text": seg.text,
            }
            for seg in segments
        ]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Raw Whisper subtitles JSON saved to: %s", path)

    # ---------- LLM scene generation ----------

    def _generate_scenes_with_llm(self, subtitles: List[SubtitleSegment]) -> List[Dict]:
        """
        Ask Gemini to:
        - Read the subtitle list
        - Group related subtitles into visual scenes
        - Ensure each scene is <= max_scene_duration_seconds (approx)
        - Ensure from/to times stay within the original SRT timeline
        - Output JSON array of scenes.
        """
        max_scene_ms = int(self.max_scene_duration_seconds * 1000)

        # Prepare a compact JSON payload for the model (more robust than raw SRT text)
        subtitle_payload = [
            {
                "index": s.index,
                "start_ms": s.start_ms,
                "end_ms": s.end_ms,
                "text": s.text,
            }
            for s in subtitles
        ]

        prompt = f"""
Bạn là một biên tập viên video chuyên nghiệp.

Nhiệm vụ:
- Dựa trên danh sách phụ đề (thời gian tính bằng mili giây) bên dưới,
  hãy chia câu chuyện thành các "cảnh" (scene) để tạo hình ảnh cho video dọc.
- Mỗi cảnh có thể gộp nhiều câu/subtitle liên tiếp có nội dung liên quan.
- Mỗi cảnh nên có độ dài tối đa khoảng {max_scene_ms} mili giây (<= {self.max_scene_duration_seconds:.1f} giây).

Yêu cầu về thời gian:
- Mỗi cảnh phải dùng mốc thời gian phù hợp với phụ đề gốc:
  - from: thời điểm bắt đầu cảnh (ms)
  - to: thời điểm kết thúc cảnh (ms)
- Các cảnh phải:
  - Liên tục theo thời gian (không có khoảng trống lớn, không bị chồng lấn)
  - from của cảnh đầu = start_ms của subtitle đầu tiên được dùng
  - to của cảnh cuối = end_ms của subtitle cuối cùng được dùng
- KHÔNG được tạo thời gian ngoài phạm vi các phụ đề gốc.

Yêu cầu về nội dung cảnh:
- Mỗi phần tử (cảnh) phải có format JSON như sau:
  {{
    "script": "toàn bộ lời thoại/giọng đọc trong cảnh, giữ nguyên tiếng Việt, ghép các câu liên quan",
    "scene": "mô tả chi tiết hình ảnh cần hiển thị (bằng tiếng Việt, mô tả khung cảnh, nhân vật, trang phục, ánh sáng, cảm xúc...)",
    "from": 0,
    "to": 7500
  }}

- "script": hãy nối các câu phụ đề nằm trong cảnh đó (cùng thứ tự thời gian).
- "scene": mô tả hình ảnh phải:
  - Rõ ràng, cụ thể, giàu chi tiết hình ảnh
  - Phù hợp với nội dung thoại
  - Phù hợp với bối cảnh văn hóa Việt Nam nếu có

ĐẦU RA:
- Trả về DUY NHẤT một mảng JSON (JSON array) các cảnh, ví dụ:
[
  {{
    "script": "...",
    "scene": "...",
    "from": 0,
    "to": 7500
  }}
]

KHÔNG thêm giải thích, KHÔNG thêm chữ nào ngoài JSON hợp lệ.
"""

        logger.info("Sending subtitles to Gemini text model to generate scenes...")
        response = self.text_model.generate_content(
            [
                "Dưới đây là danh sách phụ đề (JSON):",
                json.dumps(subtitle_payload, ensure_ascii=False),
                "\n\nHãy tạo danh sách cảnh theo đúng yêu cầu sau.\n",
                prompt,
            ]
        )

        text = (response.text or "").strip()
        logger.debug("Raw LLM scene response (first 500 chars): %s", text[:500])

        # Try to extract JSON block if model wraps with ```json ... ```
        if "```json" in text:
            text = text.split("```json", 1)[1]
            text = text.split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1]
            text = text.split("```", 1)[0].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM scene JSON: %s", e)
            logger.error("LLM response text: %s", text)
            raise ValueError("Failed to parse LLM scene JSON output") from e

        if not isinstance(data, list):
            raise ValueError("LLM scene output must be a JSON array")

        return data

    # ---------- Normalization ----------

    def _seconds_to_milliseconds(self, seconds_value: float) -> int:
        """Convert seconds (float) to integer milliseconds"""
        return int(round(seconds_value * 1000))

    def _validate_and_normalize(self, scripts_data: List[Dict]) -> List[Dict]:
        """
        Validate and normalize script data to the canonical structure used
        by the rest of the pipeline.

        Expected input fields (per item):
        - script: str
        - scene: str (visual description)
        - from: number (ms or seconds)
        - to: number (ms or seconds)
        """
        normalized: List[Dict] = []

        for i, item in enumerate(scripts_data):
            if not all(key in item for key in ["script", "from", "to"]):
                logger.warning("Skipping item %d: missing required fields", i)
                continue

            # Scene description: can be under "scene" or "sence" (typo-tolerant)
            scene_value = item.get("scene") or item.get("sence") or ""

            # Convert times to float if they're strings
            from_time = item["from"]
            to_time = item["to"]

            try:
                if isinstance(from_time, str):
                    from_time = float(from_time.strip())
                if isinstance(to_time, str):
                    to_time = float(to_time.strip())
            except Exception:
                logger.warning("Item %d: invalid time values, skipping", i)
                continue

            # Heuristic: if values are small (< 1e5), treat as seconds; otherwise as ms
            # This keeps compatibility whether the LLM returns seconds or ms.
            if abs(float(from_time)) < 1e5 and abs(float(to_time)) < 1e5:
                from_ms = self._seconds_to_milliseconds(float(from_time))
                to_ms = self._seconds_to_milliseconds(float(to_time))
            else:
                from_ms = int(round(float(from_time)))
                to_ms = int(round(float(to_time)))

            if from_ms >= to_ms:
                logger.warning("Item %d: from_ms >= to_ms, adjusting end time by +10ms", i)
                to_ms = from_ms + 10

            duration_ms = to_ms - from_ms

            normalized.append(
                {
                    "script": str(item.get("script", "")),
                    "scene": str(scene_value),
                    "from": from_ms,
                    "to": to_ms,
                    "duration": duration_ms,
                    "from_seconds": from_ms / 1000.0,
                    "to_seconds": to_ms / 1000.0,
                    "duration_seconds": duration_ms / 1000.0,
                }
            )

        if not normalized:
            raise ValueError("No valid scenes after normalization")

        # Sort by start time to enforce ordering
        normalized.sort(key=lambda x: x["from"])
        return normalized



