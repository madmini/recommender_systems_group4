from django.apps import AppConfig

from util.data import Data


class DjangoOldAppConfig(AppConfig):
    name = 'django_app_old'

    def ready(self):
        pass
