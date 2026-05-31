import asyncio
import os
from src.utils import logger
import edge_tts

AUDIO_PATH = r'D:\UserData\27149\Documents\shp\ai-video-generator\output\audio\voice.mp3'

class TtsGenerator:
    def execute(self, segments, config, output_path):
        logger.info("Generating TTS audio for %d segments", len(segments))
        voice = config.get("audio", {}).get("voice", "zh-CN-XiaoxiaoNeural")
        rate = config.get("audio", {}).get("rate", "+0%")
        text = "\uFF0C".join([seg.text for seg in segments])
        asyncio.run(self._gen(text, voice, rate, AUDIO_PATH))
        logger.info("TTS audio saved: %s", AUDIO_PATH)
        return AUDIO_PATH

    async def _gen(self, text, voice, rate, path):
        c = edge_tts.Communicate(text, voice, rate=rate)
        await c.save(path)
