"""AI Video Generator module.

Generates dance/motion videos using SiliconFlow API (Wan2.2-T2V, Wan2.2-I2V).
"""

import json
import os
import time
import urllib.request
import ssl
from src.utils import ensure_dir, get_project_path, logger

OUTPUT_DIR = str(get_project_path('output/ai_videos'))
API_BASE = 'https://api.siliconflow.cn/v1'


class AiVideoGenerator:
    """Generate videos from text or images via SiliconFlow API."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.ctx = ssl.create_default_context()

    def execute(self, prompt, config, image_path=None):
        """Generate video from prompt (and optionally an image).

        Args:
            prompt: Text description of the video.
            config: Configuration dict.
            image_path: Optional path to reference image for I2V.

        Returns:
            Path to the downloaded video file, or None.
        """
        logger.info("Generating AI video...")
        logger.info("Prompt: %s", prompt[:80])

        ensure_dir(OUTPUT_DIR)

        if image_path:
            return self._generate_i2v(prompt, image_path, config)
        else:
            return self._generate_t2v(prompt, config)

    def _generate_t2v(self, prompt, config):
        """Text-to-Video generation using Wan2.2-T2V."""
        model = config.get("ai_video", {}).get("t2v_model", "Wan-AI/Wan2.2-T2V-A14B")
        size = config.get("ai_video", {}).get("size", "1280x720")

        logger.info("Using Text-to-Video model: %s", model)

        # Submit task
        request_id = self._submit_video_task(prompt, model, size)
        if not request_id:
            logger.error("Video task submission failed")
            return None

        # Poll for result
        return self._poll_video_result(request_id)

    def _generate_i2v(self, prompt, image_path, config):
        """Image-to-Video generation using Wan2.2-I2V."""
        model = config.get("ai_video", {}).get("i2v_model", "Wan-AI/Wan2.2-I2V-A14B")
        size = config.get("ai_video", {}).get("size", "1280x720")

        logger.info("Using Image-to-Video model: %s", model)

        # Upload image first to get a URL (SiliconFlow requires image URL)
        image_url = self._upload_image(image_path)
        if not image_url:
            logger.warning("Image upload failed, falling back to T2V")
            return self._generate_t2v(prompt, config)

        # Submit I2V task
        request_id = self._submit_i2v_task(prompt, model, size, image_url)
        if not request_id:
            logger.error("I2V task submission failed")
            return None

        return self._poll_video_result(request_id)

    def _submit_video_task(self, prompt, model, size):
        """Submit a text-to-video generation task."""
        url = API_BASE + '/video/submit'
        payload = json.dumps({
            'model': model,
            'prompt': prompt,
            'video_size': size,
        }).encode('utf-8')

        return self._post_request(url, payload, 'requestId')

    def _submit_i2v_task(self, prompt, model, size, image_url):
        """Submit an image-to-video generation task."""
        url = API_BASE + '/video/submit'
        payload = json.dumps({
            'model': model,
            'prompt': prompt,
            'video_size': size,
            'image': image_url,
        }).encode('utf-8')

        return self._post_request(url, payload, 'requestId')

    def _upload_image(self, image_path):
        """Upload local image to get a URL for API use.

        SiliconFlow I2V requires an image URL. We use a data URI as fallback.
        """
        import base64
        with open(image_path, 'rb') as f:
            img_data = f.read()

        # Determine MIME type
        ext = os.path.splitext(image_path)[1].lower()
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                'webp': 'image/webp'}.get(ext.lstrip('.'), 'image/png')

        # Create data URI (works for most APIs)
        b64 = base64.b64encode(img_data).decode('ascii')
        data_uri = 'data:%s;base64,%s' % (mime, b64)
        logger.info("Image encoded as data URI (%d bytes)", len(img_data))
        return data_uri

    def _poll_video_result(self, request_id, max_wait=600, interval=10):
        """Poll for video generation result.

        Args:
            request_id: The task request ID.
            max_wait: Maximum wait time in seconds.
            interval: Polling interval in seconds.

        Returns:
            Path to downloaded video, or None.
        """
        logger.info("Waiting for video generation (requestId: %s)...", request_id)

        # Try multiple status endpoint patterns
        status_urls = [
            API_BASE + '/video/status/' + request_id,
            API_BASE + '/video/query/' + request_id,
            API_BASE + '/video/result/' + request_id,
        ]

        elapsed = 0
        while elapsed < max_wait:
            time.sleep(interval)
            elapsed += interval

            for status_url in status_urls:
                try:
                    req = urllib.request.Request(status_url, headers={
                        'Authorization': 'Bearer ' + self.api_key,
                        'User-Agent': 'AiVideoGenerator/1.0'
                    })
                    resp = urllib.request.urlopen(req, context=self.ctx, timeout=30)
                    result = json.loads(resp.read())

                    status = result.get('status', '').lower()
                    logger.info("Poll [%ds]: status=%s", elapsed, status)

                    if status in ('succeeded', 'completed', 'success'):
                        video_url = self._extract_video_url(result)
                        if video_url:
                            return self._download_video(video_url)
                        logger.warning("Succeeded but no video URL found")
                        logger.info("Result: %s", json.dumps(result)[:500])
                        return None

                    if status in ('failed', 'error'):
                        logger.error("Video generation failed: %s", result.get('error', ''))
                        return None

                    # If we got a valid response, don't try other endpoints
                    break
                except Exception as e:
                    continue

        logger.error("Video generation timed out after %ds", max_wait)
        return None

    def _extract_video_url(self, result):
        """Extract video URL from API response."""
        # Try different response formats
        if 'output' in result:
            out = result['output']
            if isinstance(out, dict):
                return out.get('video_url') or out.get('url')
            if isinstance(out, list) and out:
                return out[0] if isinstance(out[0], str) else out[0].get('url')
        if 'video_url' in result:
            return result['video_url']
        if 'results' in result:
            results = result['results']
            if isinstance(results, list) and results:
                return results[0].get('url') or results[0].get('video_url')
        return None

    def _download_video(self, url):
        """Download video from URL to local file."""
        timestamp = int(time.time())
        local_path = os.path.join(OUTPUT_DIR, 'ai_video_%d.mp4' % timestamp)
        logger.info("Downloading video from: %s", url[:80])
        req = urllib.request.Request(url, headers={'User-Agent': 'AiVideoGenerator/1.0'})
        resp = urllib.request.urlopen(req, context=self.ctx, timeout=120)
        with open(local_path, 'wb') as f:
            f.write(resp.read())
        sz = os.path.getsize(local_path)
        logger.info("Video downloaded: %s (%.1f MB)", local_path, sz / 1024 / 1024)
        return local_path

    def _post_request(self, url, payload, success_field):
        """Make a POST request and extract a field from the response."""
        req = urllib.request.Request(url, data=payload, headers={
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'AiVideoGenerator/1.0'
        })
        try:
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=30)
            data = json.loads(resp.read())
            return data.get(success_field)
        except Exception as e:
            logger.error("API error: %s", e)
            if hasattr(e, 'read'):
                logger.error("Response: %s", e.read().decode('utf-8', errors='replace')[:300])
            return None
