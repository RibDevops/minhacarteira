from django.apps import AppConfig


class CalConfig(AppConfig):
    name = 'cal'

    def ready(self):
        import cal.signals
