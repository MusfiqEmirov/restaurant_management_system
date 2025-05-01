from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project_apps.accounts'

    def ready(self):
        import project_apps.accounts.signals
