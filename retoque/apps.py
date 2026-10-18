from django.apps import AppConfig


class RetoqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'retoque'

    def ready(self):
        import retoque.signals
