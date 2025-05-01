from django.db.models.signals import post_save
from django.dispatch import receiver

from project_apps.accounts.models import User
from .models import Notification, DiscountCode, AdminCode
from .tasks import send_discount_code_email, send_admin_code_email
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

@receiver(post_save, sender=User)
def create_discount_or_admin_code(sender, instance, created, **kwargs):
    if created and not instance.is_deleted:
        if instance.role == "customer":
            discount_code = DiscountCode.objects.create(user=instance)
            send_discount_code_email.delay(instance.id, discount_code.id)
            logging.info(f"Endirim kodu yaradildi: {instance.email}")
        elif instance.role == "admin":
            admin_code = AdminCode.objects.create(user=instance)
            send_admin_code_email.delay(instance.id, admin_code.id)
            logging.info(f"Admin kodu yaradildi: {instance.email}")
            logging.info(f"Admin kodu gonderildi: {instance.email}, kod: {admin_code.code}")

@receiver(post_save, sender=Notification)
def log_notification_creation(sender, instance, created, **kwargs):
    if created:
        logging.info(f"Yeni bildiris yaradildi: {instance.user.email}, basliq: {instance.title}")            