import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diplom_project.settings')

# Создаем экземпляр.
app = Celery('diplom_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
# Загружайте модули задач из всех зарегистрированных приложений Django.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
