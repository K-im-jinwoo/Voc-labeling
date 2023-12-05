from django.apps import AppConfig
from django.conf import settings


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    # 할당 상태 자동 리셋
    def ready(self):
        if settings.SCHEDULER_DEFAULT:
            from . import operator
            operator.start()