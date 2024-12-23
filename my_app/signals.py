from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from my_app.models import ConfirmEmailToken, CustomUser
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from urllib.parse import quote

User = get_user_model()

new_user_registered = Signal()  # Уведомляет о создании нового пользователя.
new_order = Signal()  # Уведомляет о создании нового заказа.

pre_password_reset = Signal()  # providing_args=["user", "reset_password_token"]
post_password_reset = Signal()  # providing_args=["user", "reset_password_token"]


@receiver(post_save, sender=CustomUser)
def authorization(sender, instance, created, **kwargs):
    """
    Для авторизации пользователя.

    :param sender: Класс представления (View), который послал сигнал. В данном случае, CustomUser.
    :param instance: Экземпляр класса CustomUser.
    :param created: Булево значение, указывающее, был ли объект только что создан (True).
    :param kwargs: Дополнительные аргументы, которые могут быть переданы вместе с сигналом.
    :return: None
    """

    if created:
        # Генерируем и сохраняем токен подтверждения.
        token = ConfirmEmailToken.objects.create(user=instance)
        email = instance.email

        print(f'{token} сгенерирован.')
        print('')

        # Создаём ссылку подтверждения.
        confirmation_link = f"http://127.0.0.1:8000/api/v1/user/confirm-email/?token={quote(token.key)}&email={quote(email)}"

        # Отправляем электронное письмо со ссылкой для подтверждения.
        subject = 'Пожалуйста, подтвердите свой адрес электронной почты'
        message = f'Чтобы подтвердить свой адрес электронной почты, перейдите по этой ссылке: {confirmation_link}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])
        print('Письмо пользователю отправлено.')
        print('')


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    Отправляем письмо при изменении статуса заказа.

    :param user_id: ID пользователя
    :param kwargs: Дополнительные параметры
    :return: None
    """
    # send an e-mail to the user
    user = CustomUser.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Обновление статуса заказа",
        # message:
        'Заказ сформирован',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()


@receiver(pre_password_reset)
def handle_pre_password_reset(sender, **kwargs):
    """
    Обработка события предсброса пароля пользователя.

    :param sender: Объект, отправляющий сигнал
    :param kwargs: Словарь дополнительных аргументов
    :param kwargs['user']: Модель пользователя, для которого запущен процесс сброса пароля
    :return: None
    """
    user = kwargs['user']
    print(f"Процесс сброса пароля запущен для пользователя: {user}")

@receiver(post_password_reset)
def handle_post_password_reset(sender, **kwargs):
    """
    Обработка события после сброса пароля пользователя.

    :param sender: Объект, отправляющий сигнал (обычно модель User)
    :param kwargs: Словарь дополнительных аргументов
    :param kwargs['user']: Модель пользователя, для которого был успешно сброшен пароль
    :return: None
    """
    user = kwargs['user']
    print(f"Процесс сброса пароля для пользователя завершен: {user}")
