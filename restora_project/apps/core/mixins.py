from django.db import models

class TimestampMixin(models.Model): # diger modellerde vaxt fieldi yazmag evezine burdan miras alacaq
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # modelin abstract oldugunu gosterir
