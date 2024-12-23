from django.apps import AppConfig


class DiplomAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_app'

    def ready(self):
        """
        импортируем сигналы
        """
        import my_app.signals
