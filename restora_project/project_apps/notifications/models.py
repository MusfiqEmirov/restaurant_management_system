import uuid
from django.db import models

from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.accounts.models import User
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

class Notification(TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Represents notifications, welcome messages, emails, promotions.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="customer"
    )
    title = models.CharField(max_length=200, verbose_name="title")
    message = models.TextField(verbose_name="message")
    is_read = models.BooleanField(default=False, verbose_name="Read")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="sent at")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(f"Notification created: {self.user.email}, title: {self.title}")

    def __str__(self):
        return f"{self.title} ({self.user.email})"

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"


class DiscountCode(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="discount_codes",
        verbose_name="customer"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        default=uuid.uuid4
    )
    is_used = models.BooleanField(default=False)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        related_name="discount_codes",
        verbose_name="notification"
    )

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = "discount code"
        verbose_name_plural = "discount codes"


class BonusPoints(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bonus_points",
        verbose_name="customer"
    )
    points = models.IntegerField(default=0)
    last_notified_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - {self.points} points"
    
    class Meta:
        verbose_name = "bonus point"
        verbose_name_plural = "bonus points"


class AdminCode(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="admin_codes",
        limit_choices_to={'is_staff': True},
        verbose_name="admin"
    )
    code = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        related_name="admin_codes",
        verbose_name="notification"
    )

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = "admin code"
        verbose_name_plural = "admin codes"


class Message(TimestampMixin, SoftDeleteMixin, models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name="sender"
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name="recipient"
    )
    content = models.TextField(verbose_name="message")
    is_read = models.BooleanField(default=False, verbose_name="Read")
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        related_name="messages",
        verbose_name="notification"
    )

    def __str__(self):
        return f"{self.sender.email} -> {self.recipient.email}: {self.content[:50]}"

    class Meta:
        verbose_name = "message"
        verbose_name_plural = "messages"
        ordering = ['-created_at']
