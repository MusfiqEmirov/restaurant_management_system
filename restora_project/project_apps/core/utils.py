from PIL import Image
import os
from django.core.files.base import ContentFile
from django.conf import settings

def create_thumbnail(image, size=(100, 100)):
    """Şəkildən kiçik şəkil (thumbnail) yaradır."""
    img = Image.open(image)
    img.thumbnail(size)
    thumb_name = f"thumb_{os.path.basename(image.name)}"
    thumb_path = os.path.join(settings.MEDIA_ROOT, 'menu-thumbnails', thumb_name)
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    img.save(thumb_path, 'JPEG')
    return os.path.join('menu-thumbnails', thumb_name)

def add_watermark(image):
    """Şəkilə watermark əlavə edir."""
    img = Image.open(image)
    # Watermark əlavə etmək üçün loqika (sadələşdirilmiş)
    watermark_path = os.path.join(settings.MEDIA_ROOT, 'watermark.png')
    if os.path.exists(watermark_path):
        watermark = Image.open(watermark_path)
        img.paste(watermark, (10, 10), watermark)
    watermarked_name = f"wm_{os.path.basename(image.name)}"
    watermarked_path = os.path.join(settings.MEDIA_ROOT, 'menu-images', watermarked_name)
    os.makedirs(os.path.dirname(watermarked_path), exist_ok=True)
    img.save(watermarked_path, 'JPEG')
    return os.path.join('menu-images', watermarked_name)