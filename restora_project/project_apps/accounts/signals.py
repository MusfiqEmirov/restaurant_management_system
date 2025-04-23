from django.db.models.signals import post_save
from django.dispatch import  receiver

from project_apps.accounts.models import User
from project_apps.core.logging import get_logger

logger = get_logger(__name__)

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        logger.info(f"yeni user yarandi: {instance.email}, Xow gelmisiz")
        