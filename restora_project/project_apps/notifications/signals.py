from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from project_apps.accounts.models import User
from .models import (Notification,
                     DiscountCode,
                     AdminCode,
                     Message
                     )
from .tasks import (send_discount_code_email,
                    send_admin_code_email,
                    send_message_notification_email
                    )
from project_apps.core.logging import get_logger

logger = get_logger(__name__)

@receiver(post_save, sender=User)
def create_discount_or_admin_code(sender, instance, created, **kwargs):
    if created and not instance.is_deleted:
        if instance.role == "customer":
            discount_code = DiscountCode.objects.create(user=instance)
            send_discount_code_email.delay(instance.id, discount_code.id)
            logger.info(f"Endirim kodu yaradildi: {instance.email}")
        elif instance.role == "admin":
            admin_code = AdminCode.objects.create(user=instance)
            send_admin_code_email.delay(instance.id, admin_code.id)
            logger.info(f"Admin kodu yaradildi: {instance.email}")
            logger.info(f"Admin kodu gonderildi: {instance.email}, kod: {admin_code.code}")

@receiver(post_save, sender=Notification)
def log_notification_creation(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Yeni bildiris yaradildi: {instance.user.email}, basliq: {instance.title}")       

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created and not instance.is_deleted:
        try:
            # Notification yaratmaq
            title = f"Yeni Mesaj: {instance.sender.email}"
            message = (
                f"hormetli {instance.recipient.email},\n\n"
                f"size {instance.sender.email} imusteriden gelen mesaj var:\n"
                f"{instance.content}\n\n"
                f"tesekkurler,\nRestoran komandası"
            )
            
            notification = Notification.objects.create(
                user=instance.recipient,
                title=title,
                message=message,
                sent_at=timezone.now()
            )
            
            # Mmesaja notification elave elemek
            instance.notification = notification
            instance.save()
            
            # task cagirilirr
            send_message_notification_email.delay(
                instance.id,
                instance.sender.email,
                instance.recipient.email,
                instance.content
            )
            
            logger.info(f"Mesaj bildirisi yaradildi {instance.sender.email} -> {instance.recipient.email}")
        except Exception as e:
            logger.error(f"xeta bas verdi mesaj bildiri yarananda {str(e)}", exc_info=True)
