from django.db import models
from django.contrib.auth.models import AbstractUser

from project_apps.core.constants import ROLE_CHOICES  # Choices for roles
from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin   

class User(TimestampMixin, SoftDeleteMixin, AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')  # User role (customer, staff, admin)
    email = models.EmailField(unique=True)  # Unique email field
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Optional phone number

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"  # String representation of the user with role display
    
class Profile(TimestampMixin, SoftDeleteMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # One-to-one relationship with User model
    address = models.TextField(blank=True, null=True)  # Optional address field
    bonus_points = models.PositiveIntegerField(default=0)  # Field to track bonus points for the user

    def __str__(self):
        return f"{self.user.username} profile"  # String representation of the profile with the user's username

    class Meta:
        verbose_name = "Profile"  # Singular name for Profile
        verbose_name_plural = "Profiles"  # Plural name for Profile
