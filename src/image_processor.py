import os
from PIL import Image, ImageEnhance
from src.utils import ensure_dir, get_project_path, logger, list_files

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
PROCESSED_DIR = str(get_project_path('output/processed'))

class ImageProcessor:
    def execute(self, images_dir, config):
        logger.info("Processing images from: %s", images_dir)
        width = config["video"]["width"]
        height = config["video"]["height"]
        image_paths = list_files(images_dir, IMAGE_EXTENSIONS)
        if not image_paths:
            logger.warning("No images found, using placeholder")
            return self._create_placeholder(width, height)
        ensure_dir(PROCESSED_DIR)
        processed = []
        for i, path in enumerate(image_paths):
            out_path = self.resize_and_crop(path, width, height, i)
            processed.append(out_path)
        logger.info("Processed %d images at %dx%d", len(processed), width, height)
        return processed

    def resize_and_crop(self, image_path, target_w, target_h, index):
        img = Image.open(image_path).convert("RGB")
        orig_w, orig_h = img.size
        ratio = target_w / target_h
        orig_ratio = orig_w / orig_h
        if orig_ratio > ratio:
            new_h, new_w = target_h, int(target_h * orig_ratio)
        else:
            new_w, new_h = target_w, int(target_w / orig_ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left, top = (new_w - target_w) // 2, (new_h - target_h) // 2
        img = img.crop((left, top, left + target_w, top + target_h))
        img = ImageEnhance.Sharpness(img).enhance(1.1)
        img = ImageEnhance.Contrast(img).enhance(1.05)
        out_path = os.path.join(PROCESSED_DIR, "frame_%04d.jpg" % index)
        img.save(out_path, "JPEG", quality=95)
        return out_path

    def _create_placeholder(self, width, height):
        ensure_dir(PROCESSED_DIR)
        colors = [(41,128,185),(39,174,96),(192,57,43),(142,68,173),(243,156,18)]
        paths = []
        for i, color in enumerate(colors):
            img = Image.new("RGB", (width, height), color)
            out_path = os.path.join(PROCESSED_DIR, "ph_%04d.jpg" % i)
            img.save(out_path, "JPEG", quality=95)
            paths.append(out_path)
        return paths
