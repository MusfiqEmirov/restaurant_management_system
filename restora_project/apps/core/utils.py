from django.utils import timezone
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

import os

from apps.core.logging import get_logger

logger = get_logger(__name__)

def add_watermark(image_path, watermark_text="Restoran", position=(10, 10)):
    """
    sekillere watermark elave elemek
    """
    try:
        image = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            font = ImageFont.load_default()
        
        draw.text(position, watermark_text, font=font, fill=(255, 255, 255, 128))
        output_path = os.path.join(settings.MEDIA_ROOT, "watermarked_" + os.path.basename(image_path))
        image.save(output_path)
        logger.info(f"Watermark added to {image_path}, {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"watermark alinmadi {image_path}: {str(e)}")
        return None
    
def create_thumbnail(image_path, size=(100, 100)):
    """
    sekilden thumbnail yaratmag.
    """
    try:
        image = Image.open(image_path)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        output_path = os.path.join(settings.MEDIA_ROOT, "thumb_" + os.path.basename(image_path))
        image.save(output_path, quality=85)
        logger.info(f"Thumbnail created for {image_path}, saved at {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to create thumbnail for {image_path}: {str(e)}")
        return None

def clean_temp_files(directory, prefix="temp_", max_age_hours=24):
    """
    Müvəqqəti faylları təmizləyir.
    """
    try:
        now = timezone.now()
        max_age = timedelta(hours=max_age_hours)
        for filename in os.listdir(directory):
            if filename.startswith(prefix):
                file_path = os.path.join(directory, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                file_mtime = timezone.make_aware(file_mtime)
                if now - file_mtime > max_age:
                    os.remove(file_path)
                    logger.info(f"Deleted temp file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to clean temp files in {directory}: {str(e)}")    