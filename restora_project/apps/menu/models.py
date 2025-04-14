from django.db import models

from apps.core.models import TimestampMixin


class Category(TimestampMixin):
    name = models.CharField(max_lenght=100, unique=True) # yalniz category adi
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class MenuItem(TimestampMixin):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu-images/', blank=True, null=True)
    is_available = models.BooleanField(default=True) # menuyda var yoxsa yoxdur deye 
    discount_percentage = models.PositiveIntegerField(default=0) #mehsula tetbiq olunan endirimler

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    def get_discounted_price(self):# bu method eger endirim tetbiq olunubsa  endirimli qiymeti qaytarsind deyedir
        if self.discount_percentage > 0:
            return self.price * (1-self.discount_percentage / 100)
        return self.price



