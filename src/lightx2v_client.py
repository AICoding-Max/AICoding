"""LightX2V client module.

Supports both self-hosted LightX2V server and the online service.
API: POST /v1/tasks/ -> poll /v1/tasks/{task_id}/status -> download /v1/tasks/{task_id}/result

Reference: https://lightx2v-en.readthedocs.io/en/latest/deploy_guides/deploy_service.html
"""

import json
import os
import time
import urllib.request
import ssl
from src.utils import ensure_dir, get_project_path, logger

OUTPUT_DIR = str(get_project_path('output/lightx2v_videos'))


class LightX2VClient:
    """Client for LightX2V video generation server.

    Supports:
      - Self-hosted LightX2V server (local or remote)
      - LightX2V online service (https://x2v.light-ai.top)
    """

    def __init__(self, server_url='http://localhost:8000'):
        """Initialize LightX2V client.

        Args:
            server_url: Base URL of the LightX2V server.
                        Default: http://localhost:8000 (self-hosted)
                        Online: https://x2v.light-ai.top
        """
        self.server_url = server_url.rstrip('/')
        self.ctx = ssl.create_default_context()

    def check_status(self):
        """Check if the LightX2V server is available and idle.

        Returns:
            dict with 'status' key ('idle', 'busy', or 'error').
        """
        url = self.server_url + '/v1/service/status'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'AiVideoGenerator/1.0'})
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=10)
            data = json.loads(resp.read())
            return data
        except Exception as e:
            logger.warning("LightX2V server not available: %s", e)
            return {'status': 'error', 'error': str(e)}

    def generate_video(self, prompt, image_path=None, negative_prompt=None,
                       target_shape=None, config=None):
        """Generate a video using LightX2V server.

        Args:
            prompt: Text description of the video to generate.
            image_path: Optional path to reference image for I2V.
            negative_prompt: Negative prompt to avoid certain features.
            target_shape: Output resolution [height, width], e.g. [720, 1280].
            config: Optional config dict for additional parameters.

        Returns:
            Path to downloaded video file, or None on failure.
        """
        logger.info("LightX2V: Generating video...")
        logger.info("Prompt: %s", prompt[:100])

        cfg = config or {}
        if negative_prompt is None:
            negative_prompt = (
                "blurry, low quality, distorted, deformed, ugly, "
                "watermark, text, logo, static, no motion"
            )
        if target_shape is None:
            target_shape = [720, 1280]

        # Step 1: Submit task
        task_id = self._submit_task(prompt, image_path, negative_prompt, target_shape)
        if not task_id:
            logger.error("LightX2V: Task submission failed")
            return None

        logger.info("LightX2V: Task submitted, id=%s", task_id)

        # Step 2: Poll for completion
        max_wait = cfg.get('lightx2v', {}).get('max_wait_seconds', 600)
        interval = cfg.get('lightx2v', {}).get('poll_interval_seconds', 5)
        result = self._poll_task(task_id, max_wait, interval)

        if not result:
            logger.error("LightX2V: Task timed out or failed")
            return None

        # Step 3: Download result video
        video_path = self._download_result(task_id)
        if video_path:
            logger.info("LightX2V: Video saved: %s", video_path)
        return video_path

    def _submit_task(self, prompt, image_path, negative_prompt, target_shape):
        """Submit a video generation task to the server.

        Returns:
            Task ID string, or None on failure.
        """
        url = self.server_url + '/v1/tasks/'
        message = {
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'image_path': image_path or '',
            'target_shape': target_shape,
        }
        payload = json.dumps(message).encode('utf-8')

        req = urllib.request.Request(url, data=payload, headers={
            'Content-Type': 'application/json',
            'User-Agent': 'AiVideoGenerator/1.0'
        })

        try:
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=30)
            data = json.loads(resp.read())
            return data.get('task_id') or data.get('id')
        except Exception as e:
            logger.error("LightX2V submit error: %s", e)
            if hasattr(e, 'read'):
                logger.error("Response: %s", e.read().decode('utf-8', errors='replace')[:300])
            return None

    def _poll_task(self, task_id, max_wait=600, interval=5):
        """Poll task status until completed or timed out.

        Returns:
            Result dict if completed, None otherwise.
        """
        elapsed = 0
        while elapsed < max_wait:
            time.sleep(interval)
            elapsed += interval

            url = self.server_url + '/v1/tasks/' + str(task_id) + '/status'
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'AiVideoGenerator/1.0'})
                resp = urllib.request.urlopen(req, context=self.ctx, timeout=15)
                data = json.loads(resp.read())
                status = data.get('status', '').lower()
                logger.info("LightX2V poll [%ds]: %s", elapsed, status)

                if status in ('completed', 'succeeded', 'success'):
                    return data
                if status in ('failed', 'error'):
                    logger.error("LightX2V task failed: %s", data.get('error', ''))
                    return None
            except Exception as e:
                logger.debug("Poll error: %s", e)

        return None

    def _download_result(self, task_id):
        """Download the generated video from the server.

        Returns:
            Path to downloaded video file, or None.
        """
        ensure_dir(OUTPUT_DIR)
        timestamp = int(time.time())
        local_path = os.path.join(OUTPUT_DIR, 'lightx2v_%d.mp4' % timestamp)

        url = self.server_url + '/v1/tasks/' + str(task_id) + '/result'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'AiVideoGenerator/1.0'})
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=120)
            with open(local_path, 'wb') as f:
                f.write(resp.read())
            sz = os.path.getsize(local_path)
            logger.info("Downloaded: %s (%.1f MB)", local_path, sz / 1024 / 1024)
            return local_path
        except Exception as e:
            logger.error("Download error: %s", e)
            return None

    def list_tasks(self):
        """List all tasks on the server.

        Returns:
            List of task dicts.
        """
        url = self.server_url + '/v1/tasks/'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'AiVideoGenerator/1.0'})
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=15)
            data = json.loads(resp.read())
            return data if isinstance(data, list) else data.get('tasks', [])
        except Exception as e:
            logger.error("List tasks error: %s", e)
            return []
