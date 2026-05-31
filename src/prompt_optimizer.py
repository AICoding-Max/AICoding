"""Prompt Optimizer module.

Uses SiliconFlow LLM (DeepSeek/Qwen) to optimize prompts for image/video generation.
Converts Chinese descriptions to high-quality English prompts for AI models.
"""

import json
import urllib.request
import ssl
from src.utils import logger

API_BASE = 'https://api.siliconflow.cn/v1'


class PromptOptimizer:
    """Optimize prompts using LLM for better image/video generation results."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.ctx = ssl.create_default_context()

    def optimize_for_image(self, chinese_desc):
        """Convert Chinese description to optimized English image prompt.

        Args:
            chinese_desc: Chinese description of the desired image.

        Returns:
            Optimized English prompt string.
        """
        system = (
            "You are an expert AI image prompt engineer. "
            "Convert the user's Chinese description into a detailed, high-quality "
            "English prompt for AI image generation (FLUX/Qwen-Image). "
            "Include: subject, clothing, pose, lighting, style, quality tags. "
            "Output ONLY the English prompt, no explanations."
        )
        return self._call_llm(system, chinese_desc)

    def optimize_for_video(self, chinese_desc, has_music=False):
        """Convert Chinese description to optimized English video prompt.

        Args:
            chinese_desc: Chinese description of the desired video.
            has_music: Whether the video should be music-driven.

        Returns:
            Optimized English prompt string.
        """
        if has_music:
            system = (
                "You are an expert AI video prompt engineer specializing in "
                "music-driven dance videos. Convert the user's Chinese description "
                "into a detailed English prompt for AI video generation (Wan2.2). "
                "Focus on: dance style, body movements, rhythm, camera angle, "
                "lighting, environment. Output ONLY the English prompt."
            )
        else:
            system = (
                "You are an expert AI video prompt engineer. "
                "Convert the user's Chinese description into a detailed English "
                "prompt for AI video generation (Wan2.2). "
                "Include: subject, action, movement, camera angle, environment, "
                "lighting, style. Output ONLY the English prompt."
            )
        return self._call_llm(system, chinese_desc)

    def optimize_for_dance(self, dance_style, character_desc):
        """Generate a dance video prompt from style and character description.

        Args:
            dance_style: Type of dance (e.g., "modern dance", "ballet", "hip-hop").
            character_desc: Description of the character.

        Returns:
            Optimized prompt for dance video generation.
        """
        user_msg = (
            "Dance style: %s\n"
            "Character: %s\n\n"
            "Generate a detailed prompt for a dance video."
        ) % (dance_style, character_desc)

        system = (
            "You are an expert at creating prompts for AI dance video generation. "
            "Create vivid, detailed descriptions that capture: "
            "1) The dancer's appearance and outfit "
            "2) Specific dance movements and transitions "
            "3) The environment and lighting "
            "4) Camera movements (tracking, close-up, wide shot) "
            "5) The mood and energy. "
            "Output a single detailed English prompt, no explanations."
        )
        return self._call_llm(system, user_msg)

    def _call_llm(self, system_msg, user_msg):
        """Call SiliconFlow LLM API.

        Uses DeepSeek V4 Flash (free tier) or configurable model.
        """
        model = "deepseek-ai/DeepSeek-V4-Flash"
        url = API_BASE + '/chat/completions'
        payload = json.dumps({
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg}
            ],
            'temperature': 0.7,
            'max_tokens': 500,
        }).encode('utf-8')

        req = urllib.request.Request(url, data=payload, headers={
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'AiVideoGenerator/1.0'
        })

        try:
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=30)
            data = json.loads(resp.read())
            content = data['choices'][0]['message']['content'].strip()
            logger.info("Prompt optimized (%d -> %d chars)", len(user_msg), len(content))
            return content
        except Exception as e:
            logger.error("LLM API error: %s", e)
            # Fallback: return original description
            return user_msg
