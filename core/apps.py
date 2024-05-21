from django.apps import AppConfig
from django.db.utils import OperationalError

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        try:
            from .scripts import loadbasedata
            loadbasedata()
        except OperationalError:
            print("basedata was not loaded")
