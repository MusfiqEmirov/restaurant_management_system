from django.db import models
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):
    ROLE_CHOICES= (
        ('customer', 'Musteri'),
        ('staft', 'Isci'),
        ('admin', 'Admin'),
    ) # secimler ucun
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

from apps.core.models import TimestampMixin    
    

class Profile(TimestampMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True, null=True)
    loyalty_points = models.PositiveIntegerField(default=0) # bonus sistemini hesablamag ucun

    def __str__(self):
        return f"{self.user.username} profili"




