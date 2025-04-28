import os
from celery import Celery

# Django ayarlarını Celery üçün təyin edirik
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restora_project.settings')

# Celery tətbiqini yaradırıq
app = Celery('restora_project')

# Django ayarlarından Celery konfiqurasiyasını yükləyirik
app.config_from_object('django.conf:settings', namespace='CELERY')

# Bütün app-lərdəki tasks.py fayllarını avtomatik tapır
app.autodiscover_tasks()