from django.db import models
from time import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


# diger modellerde vaxt fieldi yazmag evezine burdan miras alacaq
class TimestampMixin(models.Model): 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # modelin abstract oldugunu gosterir


#qeydleri silmek evezine bazada saxlayir
class SoftDeleteMixin(models.Model):
    # qeydin silinib silmediyini
    is_deleted = models.BooleanField(default=False)
    # silinme tarixini
    deleted_at = models.DateTimeField(blank=True, null=True)

    #qeydi berpa edir
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True


# admin ve iscilerin fealiyetini izlemek ucun
class AuditMixin(models.Model):
    created_by = models.ForeignKey(User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
        )
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True


