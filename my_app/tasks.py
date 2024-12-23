from celery import shared_task

from django.core.mail import send_mail
from django_rest_passwordreset.models import ResetPasswordToken
from celery import shared_task
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.conf import settings
from .signals import pre_password_reset, post_password_reset

@shared_task
def send_reset_password_email(token_id):
    """
    Эта функция отправляет электронное письмо для сброса пароля пользователю, с помощью Celery для асинхронного
    выполнения. Он извлекает информацию о пользователе из базы данных, создает содержимое электронного письма и
    отправляет его с помощью встроенной функции send_mail в Django.
    """
    try:
        token = ResetPasswordToken.objects.get(id=token_id)
        subject = "Восстановление пароля"
        message = f"Для восстановления пароля перейдите по ссылке: {token.reset_url}"
        send_mail(subject, message, 'noreply@example.com', [token.email])
    except ResetPasswordToken.DoesNotExist:
        print("Токен не найден")


@shared_task
def reset_password_task(password, token):
    """
    Сбрасывает пароль для пользователя, идентифицируемого токеном сброса пароля..

    Эта функция пытается найти действительный токен сброса пароля, соответствующий предоставленному «токену».
    Если такой токен существует и связанный с ним пользователь имеет право на сброс пароля, он приступает к проверке
    нового пароля с помощью средств проверки пароля Django. Если пароль действителен, он обновляет пароль пользователя,
    сохраняет объект пользователя, отправляет сигнал после сброса пароля и, наконец, удаляет все токены сброса пароля
    для этого пользователя..

    Parameters:
    - password (str): The new password to set for the user.
    - token (str): The unique key identifying the reset password token.
    """
    reset_password_token = ResetPasswordToken.objects.filter(key=token).first()
    if reset_password_token and reset_password_token.user.eligible_for_reset():
        pre_password_reset.send(
            sender=reset_password_task,
            user=reset_password_token.user,
            reset_password_token=reset_password_token,
        )
        try:
            validate_password(
                password,
                user=reset_password_token.user,
                password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
            )
        except ValidationError as e:
            raise ValidationError({'password': e.messages})

        reset_password_token.user.set_password(password)
        reset_password_token.user.save()
        post_password_reset.send(
            sender=reset_password_task,
            user=reset_password_token.user,
            reset_password_token=reset_password_token,
        )
        ResetPasswordToken.objects.filter(user=reset_password_token.user).delete()

    return {'status': 'OK'}


