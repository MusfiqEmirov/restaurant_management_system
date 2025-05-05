from django.db.models.signals import post_save
from django.dispatch import  receiver

from project_apps.menu.models import Category, MenuItem
from project_apps.core.logging import get_logger

logger = get_logger(__name__)

@receiver(post_save, sender=Category)
def log_category_creation(sender, instance, created, **kwargs):
    if created:
        logger.info(f"yeni categroy yadarildi {instance.name}")

@receiver(post_save, sender=MenuItem)
def log_menu_item_creation(sender, instance, created, **kwargs):
    if created:
        logger.info(f"yeni menu mehsulu yadarildi {instance.name}")
