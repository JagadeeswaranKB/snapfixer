from django.apps import AppConfig


class PassportToolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'passport_tool'

    def ready(self):
        import passport_tool.signals
