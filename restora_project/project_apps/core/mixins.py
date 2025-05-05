from django.db import models
from django.utils import timezone
from django.conf import settings


# Instead of writing time fields in other models, they will inherit from this
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the record is created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when the record is updated

    class Meta:
        abstract = True  # Indicates this is an abstract model


# Instead of deleting records, they are soft deleted (marked as deleted)
class SoftDeleteMixin(models.Model):
    # Indicates if the record is deleted or not
    is_deleted = models.BooleanField(default=False)
    # The date and time when the record was deleted
    deleted_at = models.DateTimeField(blank=True, null=True)

    # Soft delete the record (does not remove it from the database)
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    # Restore the record if previously soft deleted
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True


# To track the activities of admins and staff
class AuditMixin(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'  # This will give the reverse relation in the User model
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'  # This will give the reverse relation in the User model
    )

    class Meta:
        abstract = True
