from django.db.models.signals import post_save
from django.dispatch import receiver

from project_apps.accounts.models import User
from project_apps.core.logging import get_logger

logging = get_logger(__name__)


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        logging.info(f"yeni istifadeci yaradildi: {instance.email}")