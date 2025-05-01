from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project_apps.notifications'

    def ready(self):
        import project_apps.notifications.signals