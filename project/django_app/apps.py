from django.apps import AppConfig

from util.data import Data


class DjangoAppConfig(AppConfig):
    name = 'django_app'

    def ready(self):
        Data.init(ml_path='ml-latest-small', preload_files=True)
