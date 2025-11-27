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
        scene_prompt: Optional[str] = None,
    ):
        """
        Args:
            api_key: Gemini API key (for scene generation, not transcription)
            scripts_dir: Where to save SRT and intermediate files
            whisper_model_name: Local Whisper model name (e.g. tiny, base, small, medium, large)
            max_scene_duration_seconds: Maximum duration of one scene in seconds
            language: Hint language code for Whisper (e.g. 'vi' for Vietnamese)
            text_model_name: Optional override for Gemini text model
            scene_prompt: Optional user-provided prompt to guide scene generation
        """
        # LLM config
        genai.configure(api_key=api_key)
        self.text_model_name = text_model_name or DEFAULT_TEXT_MODEL
        self.text_model = genai.GenerativeModel(self.text_model_name)
        self.scene_prompt = scene_prompt

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
        raw_scene_groups = self._generate_scenes_with_llm(subtitle_segments)

        # 4) Process LLM output and heal timeline
        scripts_data = self._process_and_heal_scenes(raw_scene_groups, subtitle_segments)

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
        Ask Gemini to group subtitles into scenes and return the start/end indices.
        """
        max_scene_ms = int(self.max_scene_duration_seconds * 1000)

        subtitle_payload = [
            {"index": s.index, "start_ms": s.start_ms, "end_ms": s.end_ms, "text": s.text}
            for s in subtitles
        ]

        scene_prompt_instructions = ""
        if self.scene_prompt:
            scene_prompt_instructions = f"""
Định hướng sáng tạo:
- Hãy tuân thủ định hướng sau cho TOÀN BỘ câu chuyện: "{self.scene_prompt}"
- Các cảnh phải có sự liên kết về mặt hình ảnh và nội dung, tạo thành một câu chuyện thống nhất.
"""

        prompt = f"""
Bạn là một biên tập viên video và một nghệ sĩ kể chuyện bằng hình ảnh.

Nhiệm vụ:
- Dựa trên danh sách phụ đề JSON, hãy nhóm các phụ đề liên tiếp thành các "cảnh" (scenes).
- Mỗi cảnh nên có độ dài tối đa khoảng {self.max_scene_duration_seconds:.1f} giây.
- Các nhóm phụ đề phải liên tục và không chồng chéo (ví dụ: nhóm 1: index 1-3, nhóm 2: index 4-6).

{scene_prompt_instructions}

Yêu cầu về nội dung cảnh:
- "script": Nối toàn bộ nội dung "text" của các phụ đề trong nhóm lại.
- "scene": Dựa vào "script" và định hướng sáng tạo, mô tả chi tiết hình ảnh cho cảnh đó.

Yêu cầu về định dạng ĐẦU RA:
- Trả về DUY NHẤT một mảng JSON.
- Mỗi phần tử trong mảng phải có định dạng sau:
  {{
    "start_index": <chỉ số của phụ đề đầu tiên trong nhóm>,
    "end_index": <chỉ số của phụ đề cuối cùng trong nhóm>,
    "script": "<nội dung script đã nối>",
    "scene": "<mô tả hình ảnh chi tiết>"
  }}

Ví dụ đầu ra:
[
  {{
    "start_index": 1,
    "end_index": 3,
    "script": "Ngày xửa ngày xưa, ở một ngôi làng nhỏ, có một cậu bé tên là Tí.",
    "scene": "Cận cảnh một cậu bé khoảng 10 tuổi, mặc áo bà ba nâu, đang ngồi trên lưng trâu thổi sáo. Xa xa là cánh đồng lúa chín vàng và những rặng tre xanh."
  }},
  {{
    "start_index": 4,
    "end_index": 5,
    "script": "Tí rất thông minh và dũng cảm. Cậu không sợ bất cứ điều gì.",
    "scene": "Tí đang đứng trước một hang động tối tăm, tay cầm một ngọn đuốc nhỏ, vẻ mặt kiên định và tò mò."
  }}
]

QUAN TRỌNG: Chỉ trả về mảng JSON hợp lệ. KHÔNG thêm bất kỳ giải thích hay văn bản nào khác.
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

        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM scene JSON: %s", e)
            logger.error("LLM response text: %s", text)
            raise ValueError("Failed to parse LLM scene JSON output") from e

        if not isinstance(data, list):
            raise ValueError("LLM scene output must be a JSON array")

        return data

    # ---------- Normalization and Healing ----------

    def _process_and_heal_scenes(
        self,
        raw_scenes: List[Dict],
        subtitles: List[SubtitleSegment],
    ) -> List[Dict]:
        """
        Process scene groups from LLM, calculate accurate timestamps, and heal the timeline.
        """
        if not raw_scenes:
            raise ValueError("LLM returned no scenes.")
        if not subtitles:
            raise ValueError("No subtitles available to process.")

        normalized: List[Dict] = []
        subtitle_map = {s.index: s for s in subtitles}
        max_subtitle_index = len(subtitles)

        for i, item in enumerate(raw_scenes):
            if not all(key in item for key in ["start_index", "end_index", "script", "scene"]):
                logger.warning("Skipping raw scene %d: missing required fields", i)
                continue

            try:
                start_idx = int(item["start_index"])
                end_idx = int(item["end_index"])
            except (ValueError, TypeError):
                logger.warning("Skipping raw scene %d: invalid start/end index", i)
                continue

            if not (1 <= start_idx <= end_idx <= max_subtitle_index):
                logger.warning(
                    "Skipping raw scene %d: index out of bounds (start=%d, end=%d, max=%d)",
                    i, start_idx, end_idx, max_subtitle_index
                )
                continue

            start_subtitle = subtitle_map.get(start_idx)
            end_subtitle = subtitle_map.get(end_idx)

            if not start_subtitle or not end_subtitle:
                logger.warning("Skipping raw scene %d: subtitle index not found", i)
                continue

            from_ms = start_subtitle.start_ms
            to_ms = end_subtitle.end_ms

            if from_ms >= to_ms:
                logger.warning("Scene %d: from_ms >= to_ms, adjusting end time by +10ms", i)
                to_ms = from_ms + 10

            duration_ms = to_ms - from_ms

            normalized.append({
                "script": str(item.get("script", "")),
                "scene": str(item.get("scene", "")),
                "from": from_ms,
                "to": to_ms,
                "duration": duration_ms,
                "from_seconds": from_ms / 1000.0,
                "to_seconds": to_ms / 1000.0,
                "duration_seconds": duration_ms / 1000.0,
            })

        if not normalized:
            raise ValueError("No valid scenes after processing LLM output.")

        # Sort by start time to be safe
        normalized.sort(key=lambda x: x["from"])

        # --- Healing Phase ---
        healed_scenes: List[Dict] = []
        if not normalized:
            return []

        # Add the first scene as is
        healed_scenes.append(normalized[0])

        for i in range(1, len(normalized)):
            prev_scene = healed_scenes[-1]
            current_scene = normalized[i]

            # If there's a gap, move the current scene's start time to the previous scene's end time
            if current_scene["from"] > prev_scene["to"]:
                gap = current_scene["from"] - prev_scene["to"]
                logger.debug("Healing gap of %dms between scene %d and %d", gap, i, i + 1)
                current_scene["from"] = prev_scene["to"]

            # If there's an overlap, also move the start time
            elif current_scene["from"] < prev_scene["to"]:
                overlap = prev_scene["to"] - current_scene["from"]
                logger.debug("Healing overlap of %dms between scene %d and %d", overlap, i, i + 1)
                current_scene["from"] = prev_scene["to"]

            # Ensure 'to' is after 'from'
            if current_scene["to"] <= current_scene["from"]:
                current_scene["to"] = current_scene["from"] + 10  # Min duration

            # Recalculate durations
            current_scene["from_seconds"] = current_scene["from"] / 1000.0
            current_scene["to_seconds"] = current_scene["to"] / 1000.0
            current_scene["duration"] = current_scene["to"] - current_scene["from"]
            current_scene["duration_seconds"] = current_scene["duration"] / 1000.0

            healed_scenes.append(current_scene)
            
        # Ensure the last scene ends at the same time as the last subtitle
        last_subtitle_end_ms = subtitles[-1].end_ms
        if healed_scenes and healed_scenes[-1]["to"] < last_subtitle_end_ms:
            logger.debug("Extending last scene to match final subtitle end time.")
            healed_scenes[-1]["to"] = last_subtitle_end_ms
            # Recalculate final scene duration
            final_scene = healed_scenes[-1]
            final_scene["to_seconds"] = final_scene["to"] / 1000.0
            final_scene["duration"] = final_scene["to"] - final_scene["from"]
            final_scene["duration_seconds"] = final_scene["duration"] / 1000.0


        return healed_scenes



