from PIL import Image
import os
from django.core.files.base import ContentFile
from django.conf import settings

def create_thumbnail(image, size=(100, 100)):
    """Creates a thumbnail image."""
    img = Image.open(image)  # Open the original image
    img.thumbnail(size)  # Resize the image to the specified size
    thumb_name = f"thumb_{os.path.basename(image.name)}"  # Name the thumbnail
    thumb_path = os.path.join(settings.MEDIA_ROOT, 'menu-thumbnails', thumb_name)  # Define the path to save the thumbnail
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)  # Create directories if they don't exist
    img.save(thumb_path, 'JPEG')  # Save the thumbnail image in JPEG format
    return os.path.join('menu-thumbnails', thumb_name)  # Return the relative path to the thumbnail

def add_watermark(image):
    """Adds a watermark to the image."""
    img = Image.open(image)  # Open the original image
    # Logic to add watermark (simplified)
    watermark_path = os.path.join(settings.MEDIA_ROOT, 'watermark.png')  # Path to watermark image
    if os.path.exists(watermark_path):
        watermark = Image.open(watermark_path)  # Open the watermark image
        img.paste(watermark, (10, 10), watermark)  # Apply the watermark to the image at position (10, 10)
    watermarked_name = f"wm_{os.path.basename(image.name)}"  # Name the watermarked image
    watermarked_path = os.path.join(settings.MEDIA_ROOT, 'menu-images', watermarked_name)  # Path to save the watermarked image
    os.makedirs(os.path.dirname(watermarked_path), exist_ok=True)  # Create directories if they don't exist
    img.save(watermarked_path, 'JPEG')  # Save the image with watermark in JPEG format
    return os.path.join('menu-images', watermarked_name)  # Return the relative path to the watermarked image
