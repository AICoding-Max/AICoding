import os
from src.utils import logger, seconds_to_srt_time

SRT_PATH = r'D:\UserData\27149\Documents\shp\ai-video-generator\output\subtitles\subtitle.srt'

class SubtitleGenerator:
    def execute(self, segments, config, output_path):
        logger.info("Generating subtitles for %d segments", len(segments))
        lines = []
        for seg in segments:
            start = seconds_to_srt_time(seg.start_time)
            end = seconds_to_srt_time(seg.end_time)
            lines.append(str(seg.index + 1))
            lines.append("%s --> %s" % (start, end))
            lines.append(seg.text)
            lines.append("")
        with open(SRT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info("Subtitles saved: %s", SRT_PATH)
        return SRT_PATH
