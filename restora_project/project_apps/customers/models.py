from django.db import models

from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.accounts.models import User
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

class BonusTransaction(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bonus_transactions',
        verbose_name="musteri"
    )
    points = models.IntegerField(verbose_name="Xallar")  # musbet qazanma ve menfi xercleme
    description = models.CharField(max_length=200, verbose_name="Təsvir")
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='bonus_transactions',
        verbose_name="sifaris"
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(
            f"bonus emeliyati {self.user.email}, "
            f"xallar: {self.points}, tesvir: {self.description}"
        )

    def __str__(self):
        return f"{self.user.email}: {self.points} xal ({self.description})"

    class Meta:
        verbose_name = "bonus emeliyati"
        verbose_name_plural = "bonus emeliyatlari"

