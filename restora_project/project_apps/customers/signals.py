from django.db.models.signals import post_save
from django.dispatch import receiver

from project_apps.customers.models import BonusTransaction
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

@receiver(post_save, sender=BonusTransaction)
def log_bonus_transaction_creation(sender, instance, created, **kwargs):
    if created:
        logging.info(f"yeni bonus emeliiyatu {instance.user.email}, xallar: {instance.points}")