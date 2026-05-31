#!/usr/bin/env python3
import argparse, os, sys, time
from src.utils import logger, load_config
from src.script_generator import ScriptGenerator
from src.image_processor import ImageProcessor
from src.tts_generator import TtsGenerator
from src.subtitle_generator import SubtitleGenerator
from src.video_composer import VideoComposer
from src.prompt_optimizer import PromptOptimizer
from src.backend import create_backend, BackendConfig

class VideoPipeline:
    def __init__(self, config):
        self.config = config
        self.backend = create_backend(config)
        self.script_gen = ScriptGenerator()
        self.image_proc = ImageProcessor()
        self.tts_gen = TtsGenerator()
        self.subtitle_gen = SubtitleGenerator()
        self.video_composer = VideoComposer()
        api_key = BackendConfig(config).siliconflow_key
        self.prompt_opt = PromptOptimizer(api_key) if api_key else None

    def run_classic(self, topic=None, text=None):
        logger.info('Mode: Classic')
        script_text = text or topic
        if not script_text:
            logger.error('No topic')
            sys.exit(1)
        segments = self.script_gen.execute(script_text, self.config)
        images_dir = os.path.join(os.path.dirname(__file__), 'assets', 'images')
        image_paths = self.image_proc.execute(images_dir, self.config)
        audio_path = None
        if self.config.get('audio', {}).get('tts_enabled', True):
            audio_path = self.tts_gen.execute(segments, self.config, None)
        self.subtitle_gen.execute(segments, self.config, None)
        return self.video_composer.execute(image_paths, audio_path, segments, self.config, None)

    def run_dance(self, dance_style, character_desc, scene='a professional dance studio'):
        logger.info('Mode: Dance')
        prompt = '%s performing %s in %s, full body, 4K' % (character_desc, dance_style, scene)
        if self.prompt_opt and self.config.get('prompt', {}).get('optimize_video_prompt'):
            prompt = self.prompt_opt.optimize_for_dance(dance_style, character_desc)
        img_prompt = '%s in %s pose, full body' % (character_desc, dance_style)
        if self.prompt_opt:
            img_prompt = self.prompt_opt.optimize_for_image(img_prompt)
        video_path = None
        if hasattr(self.backend, 'generate_image'):
            logger.info('Generating character image...')
            character_image = self.backend.generate_image(img_prompt)
            if character_image and hasattr(self.backend, 'generate_video_i2v'):
                video_path = self.backend.generate_video_i2v(prompt, character_image)
        if not video_path:
            if hasattr(self.backend, 'generate_video_t2v'):
                video_path = self.backend.generate_video_t2v(prompt)
            elif hasattr(self.backend, 'generate_video'):
                video_path = self.backend.generate_video(prompt)
        if not video_path:
            logger.warning('AI generation failed, using local images')
            video_path = self._fallback_local_video(dance_style, character_desc, scene)
        logger.info('Dance video: %s', video_path)
        return video_path

    def run_music_dance(self, character_desc, dance_style, scene):
        logger.info('Mode: Music-Driven Dance')
        start = time.time()
        if self.prompt_opt:
            img_prompt = self.prompt_opt.optimize_for_image(character_desc + ' full body, high quality')
            dance_prompt = self.prompt_opt.optimize_for_dance(dance_style, character_desc)
        else:
            dance_prompt = '%s performing %s in %s, 4K' % (character_desc, dance_style, scene)
            img_prompt = character_desc
        character_image = None
        if hasattr(self.backend, 'generate_image'):
            character_image = self.backend.generate_image(img_prompt)
        video_path = None
        if character_image and hasattr(self.backend, 'generate_video_i2v'):
            video_path = self.backend.generate_video_i2v(dance_prompt, character_image)
        if not video_path and hasattr(self.backend, 'generate_video_t2v'):
            video_path = self.backend.generate_video_t2v(dance_prompt)
        if not video_path and hasattr(self.backend, 'generate_video'):
            video_path = self.backend.generate_video(dance_prompt)
        if not video_path:
            logger.warning('AI failed, using local images')
            video_path = self._fallback_local_video(dance_style, character_desc, scene)
        narration = '%s dance performance. %s' % (dance_style, scene)
        segments = self.script_gen.execute(narration, self.config)
        if self.config.get('audio', {}).get('tts_enabled', True):
            self.tts_gen.execute(segments, self.config, None)
        self.subtitle_gen.execute(segments, self.config, None)
        logger.info('Complete in %.1fs', time.time() - start)
        return video_path

    def _fallback_local_video(self, dance_style, character_desc, scene):
        logger.info('Using local images for dance video')
        images_dir = os.path.join(os.path.dirname(__file__), 'assets', 'images')
        image_paths = self.image_proc.execute(images_dir, self.config)
        segments = self.script_gen.execute('%s dance: %s in %s' % (dance_style, character_desc, scene), self.config)
        audio_path = None
        if self.config.get('audio', {}).get('tts_enabled', True):
            audio_path = self.tts_gen.execute(segments, self.config, None)
        self.subtitle_gen.execute(segments, self.config, None)
        out_dir = os.path.join(os.path.dirname(__file__), 'output', 'videos')
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'dance_%d.mp4' % int(time.time()))
        return self.video_composer.execute(image_paths, audio_path, segments, self.config, out_path)

def parse_args():
    p = argparse.ArgumentParser(description='AI Video Generator v2')
    p.add_argument('--topic', type=str, help='Topic')
    p.add_argument('--text', type=str, help='Script text')
    p.add_argument('--config', type=str, help='Config file')
    p.add_argument('--dance', type=str, help='Dance style')
    p.add_argument('--character', type=str, help='Character')
    p.add_argument('--scene', type=str, default='professional dance studio')
    p.add_argument('--music-dance', action='store_true', help='Music-dance mode')
    p.add_argument('--backend', type=str, help='siliconflow or lightx2v')
    return p.parse_args()

def main():
    args = parse_args()
    config = load_config(args.config)
    if args.backend:
        config['backend'] = args.backend
    pipeline = VideoPipeline(config)
    if args.music_dance and args.dance and args.character:
        video = pipeline.run_music_dance(args.character, args.dance, args.scene)
    elif args.dance:
        video = pipeline.run_dance(args.dance, args.character or 'professional dancer', args.scene)
    else:
        video = pipeline.run_classic(topic=args.topic, text=args.text)
    print('Done! -> %s' % video)

if __name__ == '__main__':
    main()
