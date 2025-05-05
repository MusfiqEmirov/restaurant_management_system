import os
from django.db import models
from django.conf import settings

from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.core.utils import add_watermark, create_thumbnail
from project_apps.core.constants import DISCOUNT_PERCENTAGES
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

# Category model to represent categories of menu items (e.g., "Starters", "Main Course", etc.)
class Category(TimestampMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=100, unique=True)  # Unique name for the category
    description = models.TextField(blank=True, null=True)  # Optional description for the category

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(f"Category created/updated: {self.name}")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    

# MenuItem model represents items on the menu, like a specific dish or drink.
class MenuItem(TimestampMixin, SoftDeleteMixin, models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')  # The category to which the item belongs
    name = models.CharField(max_length=100)  # Name of the menu item
    description = models.TextField(blank=True, null=True)  # Optional description
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the item
    image = models.ImageField(upload_to='menu-images/', blank=True, null=True)  # Optional image for the item
    thumbnail = models.ImageField(upload_to='menu-thumbnails/', blank=True, null=True, editable=False, verbose_name="Thumbnail")  # Thumbnail for the item
    is_available = models.BooleanField(default=True)  # Whether the item is available on the menu
    discount_percentage = models.PositiveIntegerField(default=0, choices=DISCOUNT_PERCENTAGES)  # Discount percentage applicable to the item

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    # Method to calculate the price after applying the discount (if any)
    def get_discounted_price(self):
        if self.discount_percentage > 0:
            return self.price * (1 - self.discount_percentage / 100)
        return self.price
    
    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
