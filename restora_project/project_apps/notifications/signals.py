from django.db.models.signals import post_save
from django.dispatch import receiver

from project_apps.notifications.models import Notification
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

@receiver(post_save, sender=Notification)
def log_notification_creation(sender, instance, created, **kwargs):
    if created:
        logging.info(f"yeni bildiris yaradildi: {instance.user.email}, başlıq: {instance.title}")