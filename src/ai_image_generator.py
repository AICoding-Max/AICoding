"""AI Image Generator module.

Generates character/person images using SiliconFlow API (Qwen-Image, FLUX, etc.).
"""

import json
import os
import time
import urllib.request
import ssl
from src.utils import logger, ensure_dir

OUTPUT_DIR = r'D:\UserData\27149\Documents\shp\ai-video-generator\output\ai_images'
API_BASE = 'https://api.siliconflow.cn/v1'


class AiImageGenerator:
    """Generate images from text prompts via SiliconFlow API."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.ctx = ssl.create_default_context()

    def execute(self, prompt, config):
        """Generate image from prompt.

        Args:
            prompt: Text description of the image to generate.
            config: Configuration dict.

        Returns:
            Path to the downloaded image file.
        """
        logger.info("Generating AI image...")
        logger.info("Prompt: %s", prompt[:80])

        model = config.get("ai_image", {}).get("model", "Qwen/Qwen-Image")
        size = config.get("ai_image", {}).get("size", "1024x1024")
        steps = config.get("ai_image", {}).get("num_inference_steps", 25)

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Call SiliconFlow image API
        image_url = self._generate_image(prompt, model, size, steps)
        if not image_url:
            logger.error("Image generation failed")
            return None

        # Download the image
        local_path = self._download_image(image_url)
        logger.info("AI image saved: %s", local_path)
        return local_path

    def _generate_image(self, prompt, model, size, steps):
        """Call SiliconFlow image generation API."""
        url = API_BASE + '/images/generations'
        payload = json.dumps({
            'model': model,
            'prompt': prompt,
            'image_size': size,
            'batch_size': 1,
            'num_inference_steps': steps,
            'guidance_scale': 7.5,
        }).encode('utf-8')

        req = urllib.request.Request(url, data=payload, headers={
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'AiVideoGenerator/1.0'
        })

        try:
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=120)
            data = json.loads(resp.read())
            images = data.get('data', [])
            if images:
                return images[0].get('url')
        except Exception as e:
            logger.error("Image API error: %s", e)
            if hasattr(e, 'read'):
                logger.error("Response: %s", e.read().decode('utf-8', errors='replace')[:300])
        return None

    def _download_image(self, url):
        """Download image from URL to local file."""
        timestamp = int(time.time())
        local_path = os.path.join(OUTPUT_DIR, 'ai_image_%d.png' % timestamp)
        req = urllib.request.Request(url, headers={'User-Agent': 'AiVideoGenerator/1.0'})
        resp = urllib.request.urlopen(req, context=self.ctx, timeout=60)
        with open(local_path, 'wb') as f:
            f.write(resp.read())
        return local_path

    def generate_batch(self, prompts, config):
        """Generate multiple images from a list of prompts.

        Args:
            prompts: List of text prompts.
            config: Configuration dict.

        Returns:
            List of paths to generated images.
        """
        paths = []
        for i, prompt in enumerate(prompts):
            logger.info("Generating image %d/%d", i + 1, len(prompts))
            path = self.execute(prompt, config)
            if path:
                paths.append(path)
            time.sleep(1)  # Rate limiting
        return paths
