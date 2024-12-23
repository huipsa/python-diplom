# Это позволит гарантировать, что приложение всегда импортируется при
# запуске Django, и Shared_task будет использовать это приложение.

from .selery import app as celery_app

__all__ = ('celery_app',)
