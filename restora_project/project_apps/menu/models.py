import os
from django.db import models
from django.conf import settings

from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.core.utils import add_watermark, create_thumbnail
from project_apps.core.constants import DISCOUNT_PERCENTAGES
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

class Category(TimestampMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=100, unique=True) # yalniz category adi
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(f"Kateqoriya yaradildi/yenilendi: {self.name}")

    class Meta:
        verbose_name = "Kateqoriya"
        verbose_name_plural = "Kateqoriyalar"
    

class MenuItem(TimestampMixin, SoftDeleteMixin, models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu-images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='menu-thumbnails/', blank=True, null=True, editable=False, verbose_name="Kiçik şəkil")
    is_available = models.BooleanField(default=True) # menuyda var yoxsa yoxdur deye 
    discount_percentage = models.PositiveIntegerField(default=0, choices=DISCOUNT_PERCENTAGES,) #mehsula tetbiq olunan endirimler

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    def get_discounted_price(self):# bu method eger endirim tetbiq olunubsa  endirimli qiymeti qaytarsind deyedir
        if self.discount_percentage > 0:
            return self.price * (1-self.discount_percentage / 100)
        return self.price
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        verbose_name = "Menyu elementi"
        verbose_name_plural = "Menyu elementleri"



