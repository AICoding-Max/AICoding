"""Video Composer module.

Composites image slideshow + audio + subtitles into final MP4.

Uses Pillow for text overlay (avoids moviepy 2.x TextClip bugs).

"""

import os

import numpy as np

from PIL import Image, ImageDraw, ImageFont

from moviepy import (

    ImageClip, AudioFileClip, CompositeAudioClip,

    concatenate_videoclips, ColorClip, VideoClip

)

from src.utils import logger

VIDEO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output', 'videos')

os.makedirs(VIDEO_DIR, exist_ok=True)

_FONT_CANDIDATES = [

    'C:/Windows/Fonts/msyh.ttc',

    'C:/Windows/Fonts/simhei.ttf',

    'C:/Windows/Fonts/simsun.ttc',

    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',

    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',

]

def _find_font():

    for fp in _FONT_CANDIDATES:

        if os.path.exists(fp):

            return fp

    return None

_FONT_PATH = _find_font()

class VideoComposer:

    def execute(self, image_paths, audio_path, subtitle_segments, config, output_path):

        logger.info("Composing video from %d images", len(image_paths))

        width = config["video"]["width"]

        height = config["video"]["height"]

        fps = config["video"]["fps"]

        dur = config["video"]["duration_per_image"]

        sub_cfg = config.get("subtitle", {})

        use_subs = sub_cfg.get("enabled", True) and subtitle_segments

        if use_subs:

            processed_paths = self._burn_subs(image_paths, subtitle_segments, width, height, dur, sub_cfg)

        else:

            processed_paths = image_paths

        video = self._build_slideshow(processed_paths, width, height, dur)

        logger.info("Slideshow duration: %.1fs", video.duration)

        audio_clips = []

        if audio_path and os.path.exists(audio_path):

            voice = AudioFileClip(audio_path)

            video = video.with_duration(max(video.duration, voice.duration))

            audio_clips.append(voice)

        bgm = self._find_bgm(config)

        if bgm:

            bgm_clip = AudioFileClip(bgm).with_volume_scaled(

                config.get("audio", {}).get("background_music_volume", 0.20)

            ).with_duration(video.duration)

            audio_clips.append(bgm_clip)

        if audio_clips:

            video = video.with_audio(CompositeAudioClip(audio_clips))

        out = output_path or os.path.join(VIDEO_DIR, "final_video.mp4")

        os.makedirs(os.path.dirname(out), exist_ok=True)

        logger.info("Exporting video: %s", out)

        video.write_videofile(out, fps=fps, codec="libx264",

                              audio_codec="aac", threads=4, preset="ultrafast", logger=None)

        video.close()

        logger.info("Video exported: %s", out)

        return out

    def _build_slideshow(self, paths, w, h, dur):

        clips = []

        for p in paths:

            clip = ImageClip(p).with_duration(dur).resized((w, h))

            def make_frame(t, c=clip):

                return c.get_frame(t)

            clips.append(VideoClip(make_frame, duration=dur))

        return concatenate_videoclips(clips, method="chain") if clips else ColorClip((w, h), color=(0, 0, 0), duration=5)

    def _burn_subs(self, image_paths, segments, w, h, dur, cfg):

        fs = cfg.get("font_size", 56)

        fc = cfg.get("font_color", "white")

        sc = cfg.get("stroke_color", "black")

        sw = cfg.get("stroke_width", 3)

        pos = cfg.get("position", "bottom")

        bm = cfg.get("bottom_margin", 180)

        font = ImageFont.truetype(_FONT_PATH, fs) if _FONT_PATH else ImageFont.load_default()

        processed = []

        for idx, img_path in enumerate(image_paths):

            t_start = idx * dur

            t_end = t_start + dur

            text = None

            for seg in segments:

                s0 = getattr(seg, "start_time", 0)

                s1 = s0 + getattr(seg, "duration", 0)

                if s0 < t_end and s1 > t_start:

                    text = getattr(seg, "text", None)

                    break

            if not text:

                processed.append(img_path)

                continue

            img = Image.open(img_path).convert("RGB").resize((w, h))

            draw = ImageDraw.Draw(img)

            bbox = draw.textbbox((0, 0), text, font=font)

            tw = bbox[2] - bbox[0]

            th = bbox[3] - bbox[1]

            x = (w - tw) // 2

            if pos == "bottom":

                y = h - bm - th

            elif pos == "top":

                y = 100

            else:

                y = (h - th) // 2

            for dx in range(-sw, sw + 1):

                for dy in range(-sw, sw + 1):

                    draw.text((x + dx, y + dy), text, font=font, fill=sc)

            draw.text((x, y), text, font=font, fill=fc)

            proc_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "processed")

            os.makedirs(proc_dir, exist_ok=True)

            proc_path = os.path.join(proc_dir, "sub_%03d.png" % idx)

            img.save(proc_path, quality=95)

            processed.append(proc_path)

        return processed

    def _find_bgm(self, config):

        if not config.get("audio", {}).get("background_music_enabled", False):

            return None

        d = os.path.join(os.path.dirname(__file__), "..", "assets", "music")

        if not os.path.exists(d):

            return None

        for f in os.listdir(d):

            if f.lower().endswith(('.mp3', '.wav', '.m4a')):

                return os.path.join(d, f)

        return None

