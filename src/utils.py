import os
import logging
import yaml
from pathlib import Path
from datetime import timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def setup_logger(name="ai_video", level=logging.INFO):
    lg = logging.getLogger(name)
    if not lg.handlers:
        h = logging.StreamHandler()
        fmt = logging.Formatter("[%(asctime)s] %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
        h.setFormatter(fmt)
        lg.addHandler(h)
    lg.setLevel(level)
    return lg

logger = setup_logger()

def load_config(config_path=None):
    if config_path is None:
        config_path = str(PROJECT_ROOT / "config" / "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    logger.info("Config loaded: %s", config_path)
    return cfg

def seconds_to_srt_time(seconds):
    td = timedelta(seconds=max(seconds, 0))
    total = int(td.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    ms = int((seconds - int(seconds)) * 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)

def srt_time_to_seconds(srt_time):
    time_part, ms_part = srt_time.split(",")
    parts = time_part.split(":")
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    ms = int(ms_part)
    return h * 3600 + m * 60 + s + ms / 1000.0

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def get_project_path(relative_path):
    return PROJECT_ROOT / relative_path

def list_files(directory, extensions=()):
    dp = Path(directory)
    if not dp.exists():
        return []
    result = []
    for f in sorted(dp.iterdir()):
        if f.is_file():
            if not extensions or f.suffix.lower() in extensions:
                result.append(str(f))
    return result
