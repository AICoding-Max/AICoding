"""Script generator module.

Splits user text into timed segments for video production.
"""

import re
from typing import List, Dict
from src.utils import logger


class ScriptSegment:
    """A single script segment with text and timing."""

    def __init__(self, index: int, text: str, duration: float = 0.0):
        self.index = index
        self.text = text.strip()
        self.duration = duration
        self.start_time = 0.0
        self.end_time = 0.0

    def __repr__(self):
        return f"Segment({self.index}, '{self.text[:20]}...', {self.duration:.1f}s)"


class ScriptGenerator:
    """Generate timed script segments from user input.

    Template Method pattern: execute() defines the pipeline.
    """

    def execute(self, text: str, config: dict) -> List[ScriptSegment]:
        """Main pipeline: clean -> split -> assign durations."""
        logger.info("Generating script from text (%d chars)", len(text))
        cleaned = self.clean_text(text)
        segments = self.split_into_segments(cleaned, config)
        segments = self.assign_durations(segments, config)
        self.log_segments(segments)
        return segments

    def clean_text(self, text: str) -> str:
        """Remove extra whitespace and normalize punctuation."""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\r\n]+', '\n', text)
        return text

    def split_into_segments(self, text: str, config: dict) -> List[ScriptSegment]:
        """Split text into segments by punctuation or newline."""
        max_chars = config.get("script", {}).get("max_chars_per_segment", 30)
        raw_parts = re.split(r'[???!?\n]', text)
        raw_parts = [p.strip() for p in raw_parts if p.strip()]

        segments = []
        idx = 0
        for part in raw_parts:
            if len(part) <= max_chars:
                segments.append(ScriptSegment(idx, part))
                idx += 1
            else:
                sub_parts = self._split_long_text(part, max_chars)
                for sp in sub_parts:
                    segments.append(ScriptSegment(idx, sp))
                    idx += 1
        return segments

    def _split_long_text(self, text: str, max_chars: int) -> List[str]:
        """Split a long text segment by commas or length."""
        parts = re.split(r'[?,?;?]', text)
        parts = [p.strip() for p in parts if p.strip()]
        result = []
        for p in parts:
            if len(p) <= max_chars:
                result.append(p)
            else:
                while len(p) > max_chars:
                    result.append(p[:max_chars])
                    p = p[max_chars:]
                if p:
                    result.append(p)
        return result if result else [text[:max_chars]]

    def assign_durations(self, segments: List[ScriptSegment],
                         config: dict) -> List[ScriptSegment]:
        """Assign duration to each segment based on character count.

        Rule: ~0.25s per Chinese char, ~0.15s per ASCII char.
        Minimum duration from config.
        """
        min_dur = config.get("script", {}).get("min_duration", 2.0)
        cumulative = 0.0
        for seg in segments:
            cn_count = len(re.findall(r'[\u4e00-\u9fff]', seg.text))
            en_count = len(seg.text) - cn_count
            dur = cn_count * 0.25 + en_count * 0.12
            dur = max(dur, min_dur)
            seg.duration = round(dur, 2)
            seg.start_time = cumulative
            cumulative += seg.duration
            seg.end_time = cumulative
        return segments

    def log_segments(self, segments: List[ScriptSegment]):
        """Log segment summary."""
        total = sum(s.duration for s in segments)
        logger.info("Script: %d segments, total %.1fs", len(segments), total)
        for s in segments:
            logger.debug("  [%d] %.1fs: %s", s.index, s.duration, s.text)
