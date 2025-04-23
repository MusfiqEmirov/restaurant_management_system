from django.db.models.signals import post_save
from django.dispatch import receiver

from project_apps.orders.models import Order, OrderItem
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

@receiver(post_save, sender=Order)
def log_order_creation(sender, instance, created, **kwargs):
    if created:
        logging.info(f"Yeni sifaris yaradildi: #{instance.id}, musteri: {instance.user.email}")

@receiver(post_save, sender=OrderItem)
def log_order_item_creation(sender, instance, created, **kwargs):
    if created:
        logging.info(f"Yeni sifaris elementi: {instance.menu_item.name}, say: {instance.quantity}")