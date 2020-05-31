from django.apps import AppConfig

from util.data import Data


class DjangoOldAppConfig(AppConfig):
    name = 'django_app_old'

    def ready(self):
        Data.init(ml_path='ml-latest-small', preload_files=True)
