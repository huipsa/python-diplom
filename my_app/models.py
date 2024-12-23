from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator

from django.db.models import Sum

from django.contrib.auth.models import Group, Permission

from datetime import timedelta


class VariationUser(models.TextChoices):  # Разновидность пользователя.
    SHOP_REPRESENTATIVE = "SHOP_REPRESENTATIVE", "Представитель магазина"
    BUYER = "BUYER", "Покупатель"


class OrderStatus(models.TextChoices):
    BASKET = "BASKET", "В корзине"
    NEW = "NEW", "Новый"
    CONFIRMED = "CONFIRMED", "Подтвержден"
    ASSEMBLER = "ASSEMBLER", "Собран"
    SENT = "SENT", "Отправлен"
    DELIVERED = "DELIVERED", "Доставлен"
    CANCELED = "CANCELED", "Отменен"
    RETURNS = "RETURNS", "Возврат"


class Shop(models.Model):
    objects = models.manager.Manager()
    AUTH_USER_MODEL ='myapp.CustomUser'
    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.OneToOneField('CustomUser', verbose_name='Пользователь',
                                blank=True, null=True,
                                on_delete=models.CASCADE, related_name='owned_shop')
    state = models.BooleanField(verbose_name='Статус', default=True)
    date_joined = models.DateTimeField(verbose_name='Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)  # Обратный порядок сортировки.

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):

    def get_by_natural_key(self, email):
        """Метод для получения объекта пользователя по его уникальному идентификатору"""
        return self.get(**{self.model.USERNAME_FIELD: email})

    def _create_user(self, email, password=None, **extra_fields):
        """Основной метод для создания пользователя."""
        # Указываем, какие поля должны быть включены в форму админки.
        fields = ('email', 'last_name', 'first_name', 'is_active', 'shop', 'is_staff',
                  'is_superuser', 'groups', 'user_permissions')
        # Проверка наличия email, если его нет, выбрасывается исключение
        if not email:
            raise ValueError('Поле email пользователя должно быть установлено')
        # Создание экземпляра пользователя с заданными параметрами.
        user = self.model(email=email, **extra_fields)
        # Установка пароля для пользователя
        user.set_password(password)
        # Сохранение пользователя в базе данных
        user.save(using=self._db)
        # Возвращение созданного пользователя
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Для создания пользователя."""
        # Установка значений полей по умолчанию
        extra_fields.setdefault('is_staff', False)  # по умолчанию имеет доступа к административной панели Django.
        extra_fields.setdefault('is_superuser', False)  # по умолчанию пользователь является суперпользователем.
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Для создания супер пользователя."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя."""
    VariationUser = models.CharField(verbose_name='Тип пользователя', choices=VariationUser.choices,
                                     max_length=20, default=VariationUser.BUYER)
    email = models.EmailField(unique=True, verbose_name='Email', blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name='Фамилия', blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя', blank=True, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    company = models.CharField(
        verbose_name='Компания', max_length=40, blank=True
    )
    position = models.CharField(
        verbose_name='Должность', max_length=40, blank=True
    )
    is_active = models.BooleanField(default=False)  # Если не активен, то не сможет авторизоваться на сайте.
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name='Дата регистрации', auto_now_add=True)
    groups = models.ManyToManyField(Group, verbose_name=_('groups'), blank=True, related_name="customuser_groups")
    user_permissions = models.ManyToManyField(Permission, verbose_name=_('user permissions'), blank=True,
                                              related_name="customuser_user_permissions")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name']  # Обязательные поля.

    def __str__(self):
        return self.email


class Category(models.Model):
    """Категория товара."""
    objects = models.manager.Manager()
    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(max_length=80, verbose_name='Название')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """Подробная информация о продукте."""
    objects = models.manager.Manager()
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]


class Parameter(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(max_length=40, verbose_name='Название')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = "Список имен параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    objects = models.manager.Manager()
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='product_parameters', blank=True,
                                     on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='product_parameters', blank=True,
                                  on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]


class Contact(models.Model):
    """Контакты пользователя."""
    objects = models.manager.Manager()
    user = models.ForeignKey(CustomUser, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):
    """Модель для хранения заказов."""
    objects = models.manager.Manager()
    user = models.ForeignKey(CustomUser, verbose_name='Пользователь',
                             related_name='orders', blank=True,
                             on_delete=models.CASCADE)
    dt = models.DateTimeField(verbose_name='Дата создания заказа', auto_now_add=True)
    state = models.CharField(verbose_name='Статус заказа', choices=OrderStatus, max_length=15)
    contact = models.ForeignKey(Contact, verbose_name='Контакт',
                                blank=True, null=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказ"
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)

    @property
    def total_quantity(self):
        return self.ordered_items.all().aggregate(total=Sum('quantity'))['total'] or 0


class OrderItem(models.Model):
    """Модель для хранения информации о заказах."""
    objects = models.manager.Manager()
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='ordered_items', blank=True,
                              on_delete=models.CASCADE)

    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', related_name='ordered_items',
                                     blank=True,
                                     on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item'),
        ]


class ConfirmEmailToken(models.Model):
    """Для создания и сохранения уникальных токенов, которые отправляются
    пользователям по электронной почте для подтверждения их адреса электронной почты"""
    # Предоставляет интерфейс для взаимодействия с базой данных.
    objects = models.manager.Manager()

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod  # для создания статических методов внутри класса.
    def generate_key():
        """Генерирует псевдослучайный код, используя os.urandom и binascii.hexlify"""
        return get_token_generator().generate_token()

    # Cвязывает каждый токен подтверждения электронной почты с конкретным пользователем.
    user = models.ForeignKey(
        CustomUser,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь, связанный с этим токеном сброса пароля.")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Когда был сгенерирован этот токен")
    )

    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Токен сброса пароля для пользователя {user}".format(user=self.user)

    def set_expiry(self, seconds):
        """Для установки срока действия для этого токена."""
        self.expires = self.created_at + timedelta(seconds=seconds)
