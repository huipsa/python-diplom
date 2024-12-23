from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from my_app.views import *

app_name = 'backend'

urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),  # Для регистрации пользователя.
    path('user/confirm-email/', ConfirmEmail.as_view(), name='confirm-email'),  # Подтверждения E-mail пользователя.
    path('user/login/', LoginAccount.as_view(), name='user-login'),  # Для авторизации пользователей.
    path('user/delete/<int:user_id>/', DeleteAccount.as_view(), name='user-delete'),  # Удаление аккаунта пользователя.
    path('user/details', AccountDetails.as_view(), name='user-details'),  # Для управления данными пользователя.

    path('user/contact', ContactView.as_view(), name='user-contact'),  # Для управления контактной информацией польз.

    # Встроенные views.
    # Посылает токен сброса пароля на электронный адрес пользователя.
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    # Проверяет действительность токена и, если все в порядке, обновляет пароль пользователя в системе.
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),

    path('shop/create', ShopCreate.as_view(), name='shop_create'),  # Создание магазина.
    path('shop/state', ShopState.as_view(), name='shop-state'),  # Класс изменения статуса магазина.

    path('price/update', PriceUpdate.as_view(), name='partner-update'),  # Для обновления прайса от поставщика.

    path('products', ProductInfoView.as_view(), name='product_search'),  # Класс для поиска товаров.
    path('shops', ShopView.as_view(), name='shops'),  # Для просмотра списка магазинов.
    path('categories', CategoryView.as_view(), name='categories'),  # Класс для просмотра категорий.

    path('order', OrderView.as_view(), name='order'),  # Для получения и размещения заказов пользователями.
    path('basket', BasketView.as_view(), name='basket'),  # Для управления корзиной покупок пользователя.

    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),  # Класс для получения заказов поставщиками.
    path('user/list/', CustomUserList.as_view(), name='custom_userList'),  # Для теста.
]
