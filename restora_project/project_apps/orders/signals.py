from django.db.models.signals import post_save
from django.dispatch import receiver

from project_apps.accounts.models import User
from project_apps.notifications.models import BonusPoints
from .models import Order, OrderItem
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

@receiver(post_save, sender=Order)
def update_bonus_points(sender, instance, created, **kwargs):
    if created and not instance.is_deleted:
        points_obj, _ = BonusPoints.objects.get_or_create(user=instance.user, is_deleted=False)
        points_obj.points += instance.calculate_bonus_points()
        points_obj.save()
        logging.info(f"Xallar elave olundu: {instance.user.email}, xal: {instance.calculate_bonus_points()}")

@receiver(post_save, sender=Order)
def log_order_creation(sender, instance, created, **kwargs):
    if created:
        logging.info(f"Yeni sifaris yaradildi: #{instance.id}, musteri: {instance.user.email}")

@receiver(post_save, sender=OrderItem)
def log_order_item_creation(sender, instance, created, **kwargs):
    if created:
        logging.info(f"Yeni sifaris elementi: {instance.menu_item.name}, say: {instance.quantity}")