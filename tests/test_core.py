import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ai_image_generator import OUTPUT_DIR as IMAGE_OUTPUT_DIR
from src.ai_video_generator import OUTPUT_DIR as VIDEO_OUTPUT_DIR
from src.backend import BackendConfig
from src.lightx2v_client import OUTPUT_DIR as LIGHTX2V_OUTPUT_DIR
from src.script_generator import ScriptGenerator, ScriptSegment
from src.subtitle_generator import SubtitleGenerator
from src.utils import PROJECT_ROOT, seconds_to_srt_time


class ScriptGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = ScriptGenerator()
        self.config = {"script": {"max_chars_per_segment": 30, "min_duration": 2.0}}

    def test_split_into_segments_supports_common_punctuation_and_newlines(self):
        segments = self.generator.execute("第一句。\n第二句！Third sentence?", self.config)

        self.assertEqual(["第一句", "第二句", "Third sentence"], [item.text for item in segments])

    def test_split_long_text_supports_chinese_comma(self):
        segments = self.generator.split_into_segments(
            "第一段很长，第二段也很长",
            {"script": {"max_chars_per_segment": 5}},
        )

        self.assertEqual(["第一段很长", "第二段也很", "长"], [item.text for item in segments])


class UtilsTest(unittest.TestCase):
    def test_seconds_to_srt_time_clamps_negative_values(self):
        self.assertEqual("00:00:00,000", seconds_to_srt_time(-0.5))

    def test_seconds_to_srt_time_formats_milliseconds(self):
        self.assertEqual("01:01:01,250", seconds_to_srt_time(3661.25))


class ConfigTest(unittest.TestCase):
    def test_environment_api_key_overrides_file_config(self):
        with patch.dict(os.environ, {"SILICONFLOW_API_KEY": "from-env"}):
            config = BackendConfig({"api": {"siliconflow_key": "from-file"}})

        self.assertEqual("from-env", config.siliconflow_key)


class OutputPathTest(unittest.TestCase):
    def test_output_paths_are_inside_project(self):
        for output_dir in (IMAGE_OUTPUT_DIR, VIDEO_OUTPUT_DIR, LIGHTX2V_OUTPUT_DIR):
            self.assertTrue(Path(output_dir).resolve().is_relative_to(PROJECT_ROOT))

    def test_subtitle_generator_creates_parent_directory(self):
        segment = ScriptSegment(0, "hello", 1.0)
        segment.end_time = 1.0
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "nested", "subtitle.srt")

            actual_path = SubtitleGenerator().execute([segment], {}, output_path)

            self.assertEqual(output_path, actual_path)
            self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main()
