from django.db import models
from django.contrib.auth.models import AbstractUser

from project_apps.core.constants import ROLE_CHOICES  # secimler ucun
from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin   


class User(TimestampMixin, SoftDeleteMixin,AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    

class Profile(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True, null=True)
    bonus_points = models.PositiveIntegerField(default=0) # bonus sistemini hesablamag ucun

    def __str__(self):
        return f"{self.user.username} profili"
    
    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profillər"




