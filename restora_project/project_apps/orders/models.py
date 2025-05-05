from django.db import models

from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.accounts.models import User
from project_apps.menu.models import MenuItem
from project_apps.core.constants import STATUS_CHOICES, PAYMENT_TYPE_CHOICES
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

class Order(TimestampMixin, SoftDeleteMixin, models.Model):
    """
    For orders and bonus systems
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
        related_name='orders', 
        verbose_name='customer'
        )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_orders',
        null=True,
        blank=True,
        verbose_name="Created by",
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="total amount",
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
        verbose_name="Payment type"
        )
    
    # 1 point for every 10 AZN
    def calculate_bonus_points(self):
        return int(self.total_amount // 10)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(
            f"Order created or updated: {self.user.email}, "
            f"Amount: {self.total_amount} AZN, Status: {self.status}"
        )
    
    def __str__(self):
        return f"Order #{self.id} ({self.user.email})"

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        indexes = [
            models.Index(fields=['user', 'is_deleted']),
        ]


class OrderItem(TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Order items
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Menu item"
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Menu item"
    )
    quantity = models.PositiveIntegerField(verbose_name="quantity")
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                verbose_name="price"
                                )
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(
            f"Order item: {self.menu_item.name}, "
            f"Quantity: {self.quantity}, Price: {self.price} AZN"
        )
    
    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"

    class Meta:
        verbose_name = "order item"
        verbose_name_plural = "order items"
