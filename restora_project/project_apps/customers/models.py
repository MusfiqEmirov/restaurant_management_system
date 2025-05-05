from django.db import models

from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.accounts.models import User
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

# Model representing a bonus transaction (earning or spending bonus points)
class BonusTransaction(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bonus_transactions',
        verbose_name="customer"
    )
    points = models.IntegerField(verbose_name="Points")  # Positive for earning, negative for spending
    description = models.CharField(max_length=200, verbose_name="Description")
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='bonus_transactions',
        verbose_name="order"
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(
            f"Bonus transaction: {self.user.email}, "
            f"points: {self.points}, description: {self.description}"
        )

    def __str__(self):
        return f"{self.user.email}: {self.points} points ({self.description})"

    class Meta:
        verbose_name = "bonus transaction"
        verbose_name_plural = "bonus transactions"
