"""netology_pd_diplom URL Configuration

Список `urlpatterns` направляет URL-адреса в представления. Для получения дополнительной информации см.
https://docs.djangoproject.com/en/2.2/topics/http/urls/ Примеры: Представления функций 1. Добавьте импорт:
из представлений импорта my_app 2. Добавьте URL-адрес в urlpatterns: path( '',views.home, name='home')
Представления на основе классов 1. Добавьте импорт: fromother_app.views import Home 2. Добавьте URL-адрес
в urlpatterns: path('', Home.as_view(), name= 'home') Включение другого URLconf 1. Импортируйте функцию include():
из django.urls import include, путь 2. Добавьте URL-адрес в urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('my_app.urls', namespace='my_app'))
]
