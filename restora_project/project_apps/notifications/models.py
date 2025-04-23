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
        logging.info(f"bildiris yaradildi: {self.user.email}, başlıq: {self.title}")

    def __str__(self):
        return f"{self.title} ({self.user.email})"

    class Meta:
        verbose_name = "bildiris"
        verbose_name_plural = "bildirisler"