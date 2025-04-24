from django.db import models

from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.accounts.models import User
from project_apps.menu.models import MenuItem
from project_apps.core.constants import STATUS_CHOICES, PAYMENT_TYPE_CHOICES
from project_apps.core.logging import get_logger

logging = get_logger(__name__)


class Order(TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Sifarisler ve bonus sistemleri ucun
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
        related_name='orders', 
        verbose_name='musteri'
        )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="umumi mebleg",
        )
    status = models.CharField(
        max_length=20,
        choices=(STATUS_CHOICES), 
        default="pending",
        verbose_name="status"
        )
    payment_type = models.CharField(
        max_length=10, 
        choices=PAYMENT_TYPE_CHOICES, 
        default='cash', 
        verbose_name="Odenis novu"
        )
    # her 10 azn ucun 1 xal sistemi
    def calculate_bonus_points(self):
        return int(self.total_amount // 10)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(
            f"sifaris yaradildi ve ya yenilendi:{self.user.email},"
            f"mebleg:{self.total_amount} azn, status:{self.status}"
        )
    
    def __str__(self):
        return f"Sifaris #{self.id} ({self.user.email})"

    class Meta:
        verbose_name = "sifaris"
        verbose_name_plural = "sifarisler"


class OrderItem(TimestampMixin, SoftDeleteMixin, models.Model):
    """
    sifaris elementleri
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Menyu elementi"
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Menyu elementi"
    )
    quantity = models.PositiveIntegerField(verbose_name="say")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    verbose_name = "qiymet"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(
            f"sifaris elementi: {self.menu_item.name}, "
            f"say: {self.quantity}, qiymet: {self.price} AZN"
        )
    
    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"

    class Meta:
        verbose_name = "sifaris elementi"
        verbose_name_plural = "sifaris elementləri"
