from django.db import models

from project_apps.accounts.models import User
from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.core.logging import get_logger
from project_apps.core.constants import ROLE_CHOICES

logger = get_logger(__name__)

class Staff(TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Represents restaurant staff members.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="user")
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='staff',
        verbose_name="Role"
    )
    is_active = models.BooleanField(default=True, verbose_name="active")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.info(f"Staff created/updated: {self.user.email}, Role: {self.role}")

    def __str__(self):
        return f"{self.user.email} ({self.role})"

    class Meta:
        verbose_name = "staff"
        verbose_name_plural = "staff members"
