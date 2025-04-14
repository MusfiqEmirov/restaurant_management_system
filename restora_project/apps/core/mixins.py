from django.db import models


# diger modellerde vaxt fieldi yazmag evezine burdan miras alacaq
class TimestampMixin(models.Model): 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # modelin abstract oldugunu gosterir
