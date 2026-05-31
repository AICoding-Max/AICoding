import os, sys, time, threading, json, requests
from flask import Flask, render_template, request, jsonify, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from src.utils import load_config
from src.script_generator import ScriptGenerator
from src.image_processor import ImageProcessor
from src.tts_generator import TtsGenerator
from src.subtitle_generator import SubtitleGenerator
from src.video_composer import VideoComposer

app = Flask(__name__)
VIDEO_DIR = os.path.join(BASE, "output", "videos")
CONFIG_FILE = os.path.join(BASE, "config", "user_settings.json")
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

default_config = {"services": [], "tts_voice": "zh-CN-XiaoxiaoNeural"}
user_config = default_config.copy()
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            user_config.update(json.load(f))
    except:
        pass

def save_config():
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_config, f, ensure_ascii=False, indent=2)

def fetch_models(api_url, api_key):
    if not api_key or not api_url:
        return {"video": [], "llm": []}
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(f"{api_url}/models", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            video, llm = [], []
            for m in data:
                model_id = m.get("id", "")
                modality = m.get("architecture", {}).get("modality", "")
                name = m.get("name", model_id)
                if any(x in model_id.lower() for x in ["video", "wan", "kling", "sora", "pika"]) or "video" in modality:
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

def gen_task(mode, data):
    global progress
    try:
        progress = {"status": "run", "msg": "Initializing...", "path": None, "pct": 5}
        
        # 获取通用参数
        duration = data.get("duration", "10")
        aspect = data.get("aspect", "9:16")
        style_prefix = data.get("style_prefix", "")
        image_size = ASPECT_MAP.get(aspect, "720x1280")
        
        # 找到有视频模型的服务
        video_svc = None
        for svc in user_config.get("services", []):
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
            progress["msg"] = "Generating video..."; progress["pct"] = 30
            prompt = build_prompt(data.get("text", ""))
            payload = {"model": video_model, "prompt": prompt, "image_size": image_size, "duration": int(duration)}
            resp = requests.post(f"{api_url}/video/generations", headers=headers, json=payload, timeout=300)
            
        elif mode == "dance":
            progress["msg"] = "Generating dance..."; progress["pct"] = 30
            style = data.get("style", "hip hop")
            char = data.get("char", "dancer")
            scene = data.get("scene", "studio")
            prompt = build_prompt(f"{char} dancing {style} in {scene}, professional dance, smooth movements, high quality")
            payload = {"model": video_model, "prompt": prompt, "image_size": image_size, "duration": int(duration)}
            resp = requests.post(f"{api_url}/video/generations", headers=headers, json=payload, timeout=300)
            
        elif mode == "i2v":
            progress["msg"] = "Converting image..."; progress["pct"] = 30
            image_url = data.get("image", "")
            motion = build_prompt(data.get("motion", "subtle movement"))
            if not image_url:
                raise Exception("需要输入图片URL")
            payload = {"model": video_model, "image": image_url, "prompt": motion, "duration": int(duration)}
            resp = requests.post(f"{api_url}/video/generations", headers=headers, json=payload, timeout=300)
        
        if resp.status_code in [200, 201]:
            result = resp.json()
            video_url = result.get("video", {}).get("url", "") or result.get("data", [{}])[0].get("url", "")
            if video_url:
                progress["msg"] = "Downloading..."; progress["pct"] = 80
                video_resp = requests.get(video_url, timeout=120)
                fname = f"{mode}_{int(time.time())}.mp4"
                out = os.path.join(VIDEO_DIR, fname)
                with open(out, 'wb') as f:
                    f.write(video_resp.content)
                progress = {"status": "done", "msg": "Complete!", "path": out, "pct": 100}
            else:
                raise Exception("No video URL in response")
        else:
            raise Exception(f"API error {resp.status_code}: {resp.text[:200]}")
            
    except Exception as e:
        progress = {"status": "err", "msg": str(e), "path": None, "pct": 0}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    global user_config
    if request.method == "POST":
        data = request.json
        if "services" in data:
            user_config["services"] = data["services"]
        if "tts_voice" in data:
            user_config["tts_voice"] = data["tts_voice"]
        save_config()
        return jsonify({"ok": True})
    return jsonify(user_config)

@app.route("/api/models")
def api_models():
    return jsonify(fetch_models(request.args.get("api_url", ""), request.args.get("api_key", "")))

@app.route("/api/gen", methods=["POST"])
def api_gen():
    global progress
    if progress.get("status") == "run":
        return jsonify({"err": "Already running"}), 400
    d = request.json
    mode = d.get("mode", "classic")
    progress = {"status": "run", "msg": "Starting...", "path": None, "pct": 0}
    threading.Thread(target=gen_task, args=(mode, d), daemon=True).start()
    return jsonify({"ok": True})

@app.route("/api/progress")
def api_progress():
    return jsonify(progress)

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
    app.run(host="0.0.0.0", port=5000, debug=False)
