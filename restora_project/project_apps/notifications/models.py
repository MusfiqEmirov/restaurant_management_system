import uuid
from django.db import models

from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.accounts.models import User
from project_apps.core.logging import get_logger

logging = get_logger(__name__)


class Notification(TimestampMixin, SoftDeleteMixin, models.Model):
    """
    bildirisler ve xos geldin mesajlari e poctlar, promosyonlar
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="musteri"
    )
    title = models.CharField(max_length=200, verbose_name="basliq")
    message = models.TextField(verbose_name="mesaj")
    is_read = models.BooleanField(default=False, verbose_name="Oxunub")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="gonderilme tarixi")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(f"bildiris yaradildi: {self.user.email}, basliq: {self.title}")

    def __str__(self):
        return f"{self.title} ({self.user.email})"

    class Meta:
        verbose_name = "bildiris"
        verbose_name_plural = "bildirisler"


class DiscountCode(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="discount_codes",
        verbose_name="bildiris"
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
        verbose_name="bildiris"
    )

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = "endirim kodu"
        verbose_name_plural = "endirim kodlari"


class BonusPoints(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bonus_points",
        verbose_name="musteri"
    )
    points = models.IntegerField(default=0)
    last_notified_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - {self.points} xal"
    
    class Meta:
        verbose_name = "bonus xal"
        verbose_name_plural = "bonus xallar"


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
        verbose_name="bildiris"
    )

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = "admin kodu"
        verbose_name_plural = "admin kodlari"

