import os, sys, time, threading, json, requests
from flask import Flask, render_template, request, jsonify, send_from_directory
from copy import deepcopy

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

app = Flask(__name__)
VIDEO_DIR = os.path.join(BASE, "output", "videos")
CONFIG_FILE = os.path.join(BASE, "config", "user_settings.json")
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

DEFAULT_CONFIG = {"services": [], "tts_voice": "zh-CN-XiaoxiaoNeural"}
config_lock = threading.RLock()
user_config = DEFAULT_CONFIG.copy()
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            user_config.update(json.load(f))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Load config error: {exc}")

def save_config():
    tmp_file = f"{CONFIG_FILE}.tmp"
    with config_lock:
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, ensure_ascii=False, indent=2)
        os.replace(tmp_file, CONFIG_FILE)

def build_url(api_url, path):
    return f"{api_url.rstrip('/')}/{path.lstrip('/')}"

def fetch_models(api_url, api_key):
    if not api_key or not api_url:
        return {"video": [], "llm": []}
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(build_url(api_url, "models"), headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if not isinstance(data, list):
                return {"video": [], "llm": []}
            video, llm = [], []
            for m in data:
                if not isinstance(m, dict):
                    continue
                model_id = str(m.get("id", ""))
                architecture = m.get("architecture") or {}
                if not isinstance(architecture, dict):
                    architecture = {}
                modality = str(architecture.get("modality", ""))
                name = m.get("name", model_id)
                if any(x in model_id.lower() for x in ["video", "wan", "kling", "sora", "pika"]) or "video" in modality.lower():
                    video.append({"id": model_id, "name": name})
                elif not any(x in model_id.lower() for x in ["tts", "speech", "voice"]):
                    llm.append({"id": model_id, "name": name})
            return {"video": video, "llm": llm}
    except Exception as e:
        print(f"Fetch models error: {e}")
    return {"video": [], "llm": []}

# 分辨率映射
ASPECT_MAP = {
    "9:16": "720x1280",
    "16:9": "1280x720",
    "1:1": "720x720"
}

progress = {}
progress_lock = threading.Lock()

def set_progress(status, msg, path=None, pct=0):
    global progress
    with progress_lock:
        progress = {"status": status, "msg": msg, "path": path, "pct": pct}

def update_progress(msg, pct):
    with progress_lock:
        progress.update({"msg": msg, "pct": pct})

def start_task():
    global progress
    with progress_lock:
        if progress.get("status") == "run":
            return False
        progress = {"status": "run", "msg": "Starting...", "path": None, "pct": 0}
        return True

def get_progress():
    with progress_lock:
        return progress.copy()

def parse_duration(value):
    duration = int(value)
    if duration < 1 or duration > 300:
        raise ValueError("时长必须在 1 到 300 秒之间")
    return duration

def extract_video_url(result):
    video = result.get("video")
    if isinstance(video, dict) and video.get("url"):
        return video["url"]
    data = result.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0].get("url", "")
    return ""

def download_video(url, out):
    try:
        with requests.get(url, timeout=120, stream=True) as resp:
            resp.raise_for_status()
            with open(out, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
    except Exception:
        if os.path.exists(out):
            os.remove(out)
        raise

def gen_task(mode, data):
    try:
        set_progress("run", "Initializing...", pct=5)
        
        # 获取通用参数
        duration = parse_duration(data.get("duration", "10"))
        aspect = data.get("aspect", "9:16")
        style_prefix = data.get("style_prefix", "")
        image_size = ASPECT_MAP.get(aspect, "720x1280")
        
        # 找到有视频模型的服务
        video_svc = None
        with config_lock:
            services = deepcopy(user_config.get("services", []))
        for svc in services:
            if svc.get("video_model"):
                video_svc = svc
                break
        
        if not video_svc:
            raise Exception("请先配置一个视频生成API并选择视频模型")
        
        api_key = video_svc.get("key", "")
        api_url = video_svc.get("url", "")
        video_model = video_svc.get("video_model", "")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        def build_prompt(base_prompt):
            if style_prefix:
                return f"{base_prompt}, {style_prefix}"
            return base_prompt
        
        if mode == "classic":
            update_progress("Generating video...", 30)
            prompt = build_prompt(data.get("text", ""))
            payload = {"model": video_model, "prompt": prompt, "image_size": image_size, "duration": duration}
            
        elif mode == "dance":
            update_progress("Generating dance...", 30)
            style = data.get("style", "hip hop")
            char = data.get("char", "dancer")
            scene = data.get("scene", "studio")
            prompt = build_prompt(f"{char} dancing {style} in {scene}, professional dance, smooth movements, high quality")
            payload = {"model": video_model, "prompt": prompt, "image_size": image_size, "duration": duration}
            
        elif mode == "i2v":
            update_progress("Converting image...", 30)
            image_url = data.get("image", "")
            motion = build_prompt(data.get("motion", "subtle movement"))
            if not image_url:
                raise Exception("需要输入图片URL")
            payload = {"model": video_model, "image": image_url, "prompt": motion, "duration": duration}
        else:
            raise ValueError("Unsupported mode")

        resp = requests.post(build_url(api_url, "video/generations"), headers=headers, json=payload, timeout=300)
        
        if resp.status_code in [200, 201]:
            result = resp.json()
            video_url = extract_video_url(result)
            if video_url:
                update_progress("Downloading...", 80)
                fname = f"{mode}_{int(time.time())}.mp4"
                out = os.path.join(VIDEO_DIR, fname)
                download_video(video_url, out)
                set_progress("done", "Complete!", path=out, pct=100)
            else:
                raise Exception("No video URL in response")
        else:
            raise Exception(f"API error {resp.status_code}: {resp.text[:200]}")
            
    except Exception as e:
        set_progress("err", str(e))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"err": "JSON body is required"}), 400
        if "services" in data and not isinstance(data["services"], list):
            return jsonify({"err": "services must be a list"}), 400
        if "services" in data and not all(isinstance(item, dict) for item in data["services"]):
            return jsonify({"err": "services must contain objects"}), 400
        if "tts_voice" in data and not isinstance(data["tts_voice"], str):
            return jsonify({"err": "tts_voice must be a string"}), 400
        with config_lock:
            if "services" in data:
                user_config["services"] = data["services"]
            if "tts_voice" in data:
                user_config["tts_voice"] = data["tts_voice"]
            save_config()
        return jsonify({"ok": True})
    with config_lock:
        return jsonify(deepcopy(user_config))

@app.route("/api/models", methods=["POST"])
def api_models():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"err": "JSON body is required"}), 400
    return jsonify(fetch_models(data.get("api_url", ""), data.get("api_key", "")))

@app.route("/api/gen", methods=["POST"])
def api_gen():
    d = request.get_json(silent=True)
    if not isinstance(d, dict):
        return jsonify({"err": "JSON body is required"}), 400
    mode = d.get("mode", "classic")
    if mode not in {"classic", "dance", "i2v"}:
        return jsonify({"err": "Unsupported mode"}), 400
    try:
        parse_duration(d.get("duration", "10"))
    except (TypeError, ValueError) as exc:
        return jsonify({"err": str(exc)}), 400
    if not start_task():
        return jsonify({"err": "Already running"}), 409
    threading.Thread(target=gen_task, args=(mode, d), daemon=True).start()
    return jsonify({"ok": True})

@app.route("/api/progress")
def api_progress():
    return jsonify(get_progress())

@app.route("/api/videos")
def api_videos():
    files = []
    if os.path.exists(VIDEO_DIR):
        for f in sorted(os.listdir(VIDEO_DIR), reverse=True)[:20]:
            if f.endswith(".mp4"):
                p = os.path.join(VIDEO_DIR, f)
                files.append({"name": f, "size": os.path.getsize(p)})
    return jsonify(files)

@app.route("/video/<fname>")
def serve_video(fname):
    return send_from_directory(VIDEO_DIR, fname)

if __name__ == "__main__":
    print("Open http://localhost:5000")
    app.run(host=os.getenv("AICODING_HOST", "127.0.0.1"), port=5000, debug=False)
