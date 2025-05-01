from django.apps import AppConfig

class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project_apps.menu'

    def ready(self):
        import project_apps.menu.signals