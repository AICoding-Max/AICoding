import os
from src.utils import ensure_dir, get_project_path, logger, seconds_to_srt_time

SRT_PATH = str(get_project_path('output/subtitles/subtitle.srt'))

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
        path = output_path or SRT_PATH
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info("Subtitles saved: %s", path)
        return path
