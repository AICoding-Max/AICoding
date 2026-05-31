import json, os, time, base64, urllib.request, ssl
from src.utils import logger, ensure_dir

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')

class BackendConfig:
    def __init__(self, config_dict=None):
        cfg = config_dict or {}
        self.backend = cfg.get('backend', 'siliconflow')
        sf = cfg.get('api', {})
        self.siliconflow_key = os.getenv('SILICONFLOW_API_KEY') or sf.get('siliconflow_key', '')
        self.siliconflow_base = sf.get('base_url', 'https://api.siliconflow.cn/v1')
        l2v = cfg.get('lightx2v', {})
        self.lightx2v_url = l2v.get('server_url', 'http://localhost:8000')
        self.lightx2v_timeout = l2v.get('max_wait_seconds', 600)
        self.lightx2v_poll = l2v.get('poll_interval_seconds', 5)
        ai_img = cfg.get('ai_image', {})
        self.image_model = ai_img.get('model', 'Qwen/Qwen-Image')
        self.image_size = ai_img.get('size', '1024x1024')
        self.image_steps = ai_img.get('num_inference_steps', 25)
        ai_vid = cfg.get('ai_video', {})
        self.t2v_model = ai_vid.get('t2v_model', 'Wan-AI/Wan2.2-T2V-A14B')
        self.i2v_model = ai_vid.get('i2v_model', 'Wan-AI/Wan2.2-I2V-A14B')
        self.video_size = ai_vid.get('size', '1280x720')
        dance = cfg.get('dance', {})
        self.dance_steps = dance.get('infer_steps', 20)
        self.dance_fps = dance.get('fps', 24)
        self.dance_resolution = dance.get('resolution', [720, 1280])

class SiliconFlowBackend:
    def __init__(self, config):
        self.cfg = config
        self.ctx = ssl.create_default_context()
        self.headers = {'Authorization': 'Bearer ' + config.siliconflow_key, 'Content-Type': 'application/json', 'User-Agent': 'AiVideoGen/2.0'}

    def generate_image(self, prompt):
        url = self.cfg.siliconflow_base + '/images/generations'
        payload = json.dumps({'model': self.cfg.image_model, 'prompt': prompt, 'image_size': self.cfg.image_size, 'batch_size': 1, 'num_inference_steps': self.cfg.image_steps, 'guidance_scale': 7.5}).encode()
        req = urllib.request.Request(url, data=payload, headers=self.headers)
        try:
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=120)
            data = json.loads(resp.read())
            images = data.get('data', [])
            if images:
                return self._download(images[0].get('url'), 'ai_image', '.png')
        except Exception as e:
            logger.error('Image error: %s', e)
        return None

    def generate_video_t2v(self, prompt):
        url = self.cfg.siliconflow_base + '/video/submit'
        payload = json.dumps({'model': self.cfg.t2v_model, 'prompt': prompt, 'video_size': self.cfg.video_size}).encode()
        rid = self._post(url, payload, 'requestId')
        return self._poll_video(rid) if rid else None

    def generate_video_i2v(self, prompt, image_path):
        img_url = self._encode_image(image_path)
        url = self.cfg.siliconflow_base + '/video/submit'
        payload = json.dumps({'model': self.cfg.i2v_model, 'prompt': prompt, 'video_size': self.cfg.video_size, 'image': img_url}).encode()
        rid = self._post(url, payload, 'requestId')
        return self._poll_video(rid) if rid else None

    def _poll_video(self, request_id):
        url = self.cfg.siliconflow_base + '/video/status'
        elapsed = 0
        while elapsed < self.cfg.lightx2v_timeout:
            time.sleep(self.cfg.lightx2v_poll)
            elapsed += self.cfg.lightx2v_poll
            try:
                payload = json.dumps({'requestId': request_id}).encode()
                req = urllib.request.Request(url, data=payload, headers=self.headers)
                resp = urllib.request.urlopen(req, context=self.ctx, timeout=30)
                result = json.loads(resp.read())
                status = result.get('status', '').lower()
                logger.info('Video poll [%ds]: %s', elapsed, status)
                if status in ('succeed', 'succeeded', 'completed'):
                    vurl = self._extract_url(result)
                    return self._download(vurl, 'ai_video', '.mp4') if vurl else None
                if status in ('failed', 'error'):
                    return None
            except Exception as e:
                logger.error('Poll error: %s', e)
                continue
        return None

    def _extract_url(self, result):
        # SiliconFlow format: results.videos[0].url
        results = result.get('results', {})
        if isinstance(results, dict):
            videos = results.get('videos', [])
            if videos and isinstance(videos[0], dict):
                return videos[0].get('url')
        # Legacy format
        if 'output' in result:
            out = result['output']
            if isinstance(out, dict):
                return out.get('video_url') or out.get('url')
            if isinstance(out, list) and out:
                return out[0] if isinstance(out[0], str) else out[0].get('url')
        return result.get('video_url')

    def _encode_image(self, path):
        with open(path, 'rb') as f:
            data = f.read()
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}.get(ext, 'image/png')
        return 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode())

    def _post(self, url, payload, field):
        req = urllib.request.Request(url, data=payload, headers=self.headers)
        try:
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=30)
            return json.loads(resp.read()).get(field)
        except Exception as e:
            logger.error('API error: %s', e)
            return None

    def _download(self, url, prefix, ext):
        ts = int(time.time())
        d = os.path.join(OUTPUT_DIR, prefix)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, '%s_%d%s' % (prefix, ts, ext))
        req = urllib.request.Request(url, headers={'User-Agent': 'AiVideoGen/2.0'})
        resp = urllib.request.urlopen(req, context=self.ctx, timeout=120)
        with open(path, 'wb') as f:
            f.write(resp.read())
        logger.info('Downloaded: %s', path)
        return path


class LightX2VBackend:
    def __init__(self, config):
        self.cfg = config
        self.ctx = ssl.create_default_context()
        self.base = config.lightx2v_url.rstrip('/')

    def is_available(self):
        try:
            req = urllib.request.Request(self.base + '/v1/service/status', headers={'User-Agent': 'AiVideoGen/2.0'})
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=10)
            return json.loads(resp.read()).get('status') != 'error'
        except Exception as exc:
            logger.debug('LightX2V availability check failed: %s', exc)
            return False

    def generate_video(self, prompt, image_path=None, negative_prompt=None):
        if not negative_prompt:
            negative_prompt = 'blurry, low quality, distorted, deformed, ugly, watermark, text, static'
        msg = {'prompt': prompt, 'negative_prompt': negative_prompt, 'image_path': self._encode_image(image_path) if image_path else '', 'target_shape': self.cfg.dance_resolution, 'seed': 42}
        payload = json.dumps(msg).encode()
        req = urllib.request.Request(self.base + '/v1/tasks/', data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'AiVideoGen/2.0'})
        try:
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=30)
            data = json.loads(resp.read())
            task_id = data.get('task_id') or data.get('id')
            logger.info('LightX2V task: %s', task_id)
            return self._poll(task_id)
        except Exception as e:
            logger.error('LightX2V error: %s', e)
            return None

    def _poll(self, task_id):
        elapsed = 0
        while elapsed < self.cfg.lightx2v_timeout:
            time.sleep(self.cfg.lightx2v_poll)
            elapsed += self.cfg.lightx2v_poll
            try:
                req = urllib.request.Request(self.base + '/v1/tasks/' + str(task_id) + '/status', headers={'User-Agent': 'AiVideoGen/2.0'})
                resp = urllib.request.urlopen(req, context=self.ctx, timeout=15)
                data = json.loads(resp.read())
                status = data.get('status', '').lower()
                logger.info('LightX2V poll [%ds]: %s', elapsed, status)
                if status in ('completed', 'succeeded'):
                    return self._download_result(task_id)
                if status in ('failed', 'error'):
                    return None
            except Exception as exc:
                logger.debug('LightX2V poll error: %s', exc)
                continue
        return None

    def _download_result(self, task_id):
        ts = int(time.time())
        d = os.path.join(OUTPUT_DIR, 'lightx2v')
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, 'lightx2v_%d.mp4' % ts)
        try:
            req = urllib.request.Request(self.base + '/v1/tasks/' + str(task_id) + '/result', headers={'User-Agent': 'AiVideoGen/2.0'})
            resp = urllib.request.urlopen(req, context=self.ctx, timeout=120)
            with open(path, 'wb') as f:
                f.write(resp.read())
            logger.info('Downloaded: %s', path)
            return path
        except Exception as e:
            logger.error('Download error: %s', e)
            return None

    def _encode_image(self, path):
        if not path or not os.path.exists(path):
            return ''
        with open(path, 'rb') as f:
            data = f.read()
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}.get(ext, 'image/png')
        return 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode())


def create_backend(config):
    cfg = BackendConfig(config)
    if cfg.backend == 'lightx2v':
        backend = LightX2VBackend(cfg)
        if backend.is_available():
            logger.info('Using LightX2V: %s', cfg.lightx2v_url)
            return backend
        logger.warning('LightX2V not available, using SiliconFlow')
    logger.info('Using SiliconFlow backend')
    return SiliconFlowBackend(cfg)
