import asyncio
import os
from src.utils import ensure_dir, get_project_path, logger
import edge_tts

AUDIO_PATH = str(get_project_path('output/audio/voice.mp3'))

class TtsGenerator:
    def execute(self, segments, config, output_path):
        logger.info("Generating TTS audio for %d segments", len(segments))
        voice = config.get("audio", {}).get("voice", "zh-CN-XiaoxiaoNeural")
        rate = config.get("audio", {}).get("rate", "+0%")
        text = "\uFF0C".join([seg.text for seg in segments])
        path = output_path or AUDIO_PATH
        ensure_dir(os.path.dirname(path))
        asyncio.run(self._gen(text, voice, rate, path))
        logger.info("TTS audio saved: %s", path)
        return path

    async def _gen(self, text, voice, rate, path):
        c = edge_tts.Communicate(text, voice, rate=rate)
        await c.save(path)
