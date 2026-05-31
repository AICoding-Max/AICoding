import os
import subprocess
import sys
from pathlib import Path


FONT_CANDIDATES = (
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/opentype/noto/NotoSansCJK-Regular.ttc",
)


def open_path(path, platform_name=None):
    target = str(Path(path).resolve())
    if not os.path.exists(target):
        raise FileNotFoundError(target)

    current_platform = platform_name or sys.platform
    if current_platform == "win32":
        os.startfile(target)
        return
    if current_platform == "darwin":
        subprocess.run(["open", target], check=True)
        return
    subprocess.run(["xdg-open", target], check=True)


def find_font():
    configured_font = os.getenv("AICODING_FONT_PATH")
    candidates = (configured_font,) + FONT_CANDIDATES if configured_font else FONT_CANDIDATES
    for font_path in candidates:
        if os.path.isfile(font_path):
            return font_path
    return None
