from django.apps import AppConfig

from util.data import Data


class DjangoFancyAppConfig(AppConfig):
    name = 'django_app_fancy'

    def ready(self):
        Data.init(ml_path='ml-latest-small', preload_files=True)
