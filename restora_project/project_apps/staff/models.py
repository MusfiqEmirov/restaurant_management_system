from django.db import models

from project_apps.accounts.models import User
from project_apps.core.mixins import TimestampMixin, SoftDeleteMixin
from project_apps.core.logging import get_logger
from project_apps.core.constants import ROLE_CHOICES

logging = get_logger(__name__)


class Staff(TimestampMixin, SoftDeleteMixin, models.Model):
    """
    restaran iscilerini temsil eden
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="istifadeci")
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='staff',
        verbose_name="Rol"
    )
    is_active = models.BooleanField(default=True, verbose_name="aktiv")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(f"isci yaradildi/yenilendi: {self.user.email}, Rol: {self.role}")

    def __str__(self):
        return f"{self.user.email} ({self.role})"

    class Meta:
        verbose_name = "isci"
        verbose_name_plural = "isciler"