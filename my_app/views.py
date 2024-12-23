# from distutils.util import strtobool
from ast import literal_eval

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse, Http404
from django.http import HttpResponse
from requests import get
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json
from urllib.parse import quote
from yaml import load as load_yaml, Loader

from my_app.models import (Shop, CustomUser, Category, Product, ProductInfo, Parameter, ProductParameter, Order,
                           OrderItem, Contact, ConfirmEmailToken)
from my_app.serializers import (UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer,
                                OrderItemSerializer, OrderSerializer, ContactSerializer)
from my_app.signals import new_user_registered, new_order
from rest_framework.generics import GenericAPIView
from django.core.mail import send_mail
import json
from django.http import JsonResponse
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from yaml import load, Loader


class RegisterAccount(APIView):
    """
    Для регистрации пользователя путем сохранения его в б.д
    """

    def post(self, request, *args, **kwargs):
        """
            Обработайте запрос POST и создайте нового пользователя

            Args:
                request: The Django request object.

            Returns:
                JsonResponse: Ответ, указывающий статус операции и любые errors.
            """
        # проверяем обязательные аргументы
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):

            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
                email = request.data['email']
                print(f'Пользователь с почтой {email} создан')
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmEmail(APIView):
    """
    APIView для подтверждения электронной почты пользователя.
    Срабатывает от сигнала.
    При успешном подтверждении аккаунт активируется.

    Methods:
        GET: Подтверждение электронной почты через токен.
    """
    def get(self, request, *args, **kwargs):
        print(f' request {request.data}')
        email = request.query_params.get('email')
        token = request.query_params.get('token')

        print(f'Email: {email}, Token: {token}')

        if email and token:
            confirm_email_token = ConfirmEmailToken.objects.filter(user__email=email, key=token).first()
            if confirm_email_token:
                confirm_email_token.user.is_active = True
                confirm_email_token.user.save()
                confirm_email_token.delete()
                print(f'Пользователь с почтой {confirm_email_token.user.email} авторизован.')
                return Response({'Status': True})
            else:
                return Response({'Status': False, 'Errors': 'Неправильно указан токен или email'}, status=400)
        else:
            return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=400)


class LoginAccount(APIView):
    """
    Для входа в систему пользователя.
    Возвращает токен для последующего использования.

    Methods:
        POST: Аутентификация пользователя по электронной почте и паролю.
    """
    def post(self, request, *args, **kwargs):
        print('метод post LoginAccount сработал')
        """
                Authenticate a user.

                Args:
                    request (Request): The Django request object.

                Returns:
                    JsonResponse: The response indicating the status of the operation and any errors.
                """
        email = request.data.get('email')
        password = request.data.get('password')

        if not (email and password):
            return Response({"error": "Электронная почта или пароль отсутствуют в запросе."}, status=400)
        print('Электронная почта и пароль присутствуют в запросе.')

        CustomUser = get_user_model()

        # Есть ли в колонке email, email текущего пользователя.
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            print("ОТСУТСТВУЕТ ПОЧТА")
            return Response({"error": "Invalid credentials"}, status=401)
        print(user)

        # Проверяем, активен ли пользователь
        if not user.is_active:
            print("ПОЛЬЗОВАТЕЛЬ НЕ АКТИВЕН")
            return Response({"error": "User is inactive"}, status=403)
        print('Активность подтверждена')

        # Здесь мы используем check_password для проверки пароля
        if not user.check_password(password):
            print("ОТСУТСТВУЕТ ПАРОЛЬ")
            return Response({"error": "Invalid credentials"}, status=401)
        print("Проверка логин-пароль пройдена")

        # Делаем is_authenticated = True
        login(request, user)

        if request.user.is_authenticated:
            # Пользователь аутентифицирован
            print('Пользователь аутентифицирован')
            return HttpResponse("Вы вошли в систему.")
        else:
            # Пользователь не аутентифицирован
            print('Пользователь не аутентифицирован')
            return HttpResponse("Пожалуйста, войдите в систему.")

        return Response({"message": "Authentication successful"}, status=200)


class CustomUserList(APIView):  # Для теста.
    """Вывести пользователей в консоль"""

    def get(self, request):
        print('get list сработал')
        CustomUser = get_user_model()
        users = CustomUser.objects.values('id', 'email')  # Получаем список словарей

        for user in users:
            print(user)  # Выводим каждого пользователя в консоль

        return JsonResponse(list(users), safe=False)


class DeleteAccount(GenericAPIView):
    """
    Для удаления аккаунта пользователя.

    Methods:
    - get_object Находит нужный аккаунт.
    - delite: Удаляет аккаунт.

    Attributes:
    - None
    """
    # permission_classes = [IsAuthenticated]
    # любой пользователь может удалить свои данные из бд сайта.

    queryset = CustomUser.objects.all()

    def get_object(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise Http404("User does not exist")

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = self.get_object(user_id)
        user.delete()
        print('пользователь удален')
        return Response({'Status': True}, status=204)


class AccountDetails(APIView):
    """
    Класс для управления данными учетной записи пользователя.

    Methods:
    - get: Получить данные аутентифицированного пользователя.
    - post: Обновите данные учетной записи аутентифицированного пользователя...

    Attributes:
    - None
    """

    # получить данные
    def get(self, request, *args, **kwargs):
        print('AccountDetails get сработала.')
        """
               Получить данные аутентифицированного пользователя.

               Args:
               - request (Request): The Django request object.

               Returns:
               - Response: Ответ, содержащий данные аутентифицированного пользователя..
        """

        # Берем из запроса параметры для авторизации.
        email = request.query_params.get('email')
        password = request.query_params.get('password')
        user = authenticate(request, username=email, password=password)
        print(user)
        request.user = user

        # Проверка на аутентификацию пользователя.
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Пользователь не аутентифицирован'}, status=401)
        print(f'Пользователь {user} аутентифицирован')

        serializer = UserSerializer(request.user)
        
        # Выводим данные в консоль
        data = serializer.data  # Получаем данные из сериализатора
        print("User Data:", data)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        print('AccountDetails post сработал')
        if 'email' not in request.data:
            return JsonResponse({'Status': False, 'Error': 'Email is required'}, status=400)
        email = request.data['email']
        try:
            user = CustomUser.objects.get(email=email)
        except ObjectDoesNotExist:
            return JsonResponse({'Status': False, 'Error': 'User does not exist'}, status=404)
        if not user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if 'password' in request.data:
            print('Пароль есть')
            errors = {}
            try:
                validate_password(request.data['password'])
                print('Пароль норм.')
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(str(item))
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user.shop_id = request.data.get('shop_id', None)
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class ContactView(APIView):
    """
       Класс для управления контактной информацией.

       Methods:
       - get: Retrieve the contact information of the authenticated user.
       - post: Create a new contact for the authenticated user.
       - put: Update the contact information of the authenticated user.
       - delete: Delete the contact of the authenticated user.

       Attributes:
       - None
       """

    # получить мои контакты
    def get(self, request, *args, **kwargs):
        """
               Retrieve the contact information of the authenticated user.

               Args:
               - request (Request): The Django request object.

               Returns:
               - Response: The response containing the contact information.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(
            user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    # добавить новый контакт
    def post(self, request, *args, **kwargs):
        """
               Create a new contact for the authenticated user.

               Args:
               - request (Request): The Django request object.

               Returns:
               - JsonResponse: The response indicating the status of the operation and any errors.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить контакт
    def delete(self, request, *args, **kwargs):
        """
               Delete the contact of the authenticated user.

               Args:
               - request (Request): The Django request object.

               Returns:
               - JsonResponse: The response indicating the status of the operation and any errors.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # редактировать контакт
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            """
                   Update the contact information of the authenticated user.

                   Args:
                   - request (Request): The Django request object.

                   Returns:
                   - JsonResponse: The response indicating the status of the operation and any errors.
                   """
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ShopCreate(APIView):
    """
    Для регистрации нового магазина.

    Methods:
    POST: Создание магазина.
    """
    def post(self, request, *args, **kwargs):
        print('ShopCreate post сработала')
        print(request.data)

        if 'email' not in request.data:
            return JsonResponse({'Status': False, 'Error': 'Требуется Email'}, status=400)
        email = request.data['email']
        try:
            user = CustomUser.objects.get(email=email)
        except ObjectDoesNotExist:
            return JsonResponse({'Status': False, 'Error': 'Пользователь не существует'}, status=404)
        if not user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if 'password' in request.data:
            print('Пароль есть')
            errors = {}
            try:
                validate_password(request.data['password'])
                print('Пароль норм.')
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(str(item))
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
        serializer = ShopSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShopState(APIView):
    """
       Класс для управления состоянием партнера.

       Methods:
       - get: Retrieve the state of the partner.

       Attributes:
       - None
       """

    # Получить текущий статус магазина.
    def get(self, request, *args, **kwargs):
        print('PartnerState get')
        """
               Retrieve the state of the partner.

               Args:
               - request (Request): The Django request object.

               Returns:
               - Response: The response containing the state of the partner.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # Изменить текущий статус магазина.
    def post(self, request, *args, **kwargs):
        """
               Обновить статус партнера.

               Args:
               - request (Request): The Django request object.

               Returns:
               - JsonResponse: The response indicating the status of the operation and any errors.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=literal_eval(state))
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PriceUpdate(APIView):
    """
    Класс для обновления прайса от поставщика.

    Methods:
    - post: Update the partner information.

    Attributes:
    - None
    """

    def post(self, request, *args, **kwargs):
        """
                Update the partner price list information.

                Args:
                - request (Request): The Django request object.

                Returns:
                - JsonResponse: The response indicating the status of the operation and any errors.
                """
        print('PriceUpdate post сработал.')

        # Берем из запроса параметры для авторизации.
        email = request.data.get('email')
        password = request.data.get('password')
        print(f'логин: {email}, пароль: {password}')
        user = authenticate(request, username=email, password=password)
        print(f'юзер: {user}')
        request.user = user

        # Проверка пользователя на аутентификацию.
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        print('Пользователь аутентифицирован.')

        # Проверка на тип пользователя, магазин или нет.
        if request.user.VariationUser != 'SHOP_REPRESENTATIVE':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        print('пользователь-магазин')

        # Является ли предоставленный URL действительным.
        url = request.data.get('url')
        if url:
            # Создание экземпляра класса для валидации URL
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                print(f'url {url} валиден')
                stream = get(url).content
                print(f'stream: {stream}')

                data = load_yaml(stream, Loader=Loader)

                shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                print('Загрузка успешна.')
                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ProductInfoView(APIView):
    """
        Класс для поиска товаров.

        Methods:
        - get: Retrieve the product information based on the specified filters.

        Attributes:
        - None
        """

    def get(self, request: Request, *args, **kwargs):
        """
               Получить информацию о продукте на основе указанных фильтров..

               Args:
               - request (Request): The Django request object.

               Returns:
               - Response: The response containing the product information.
               """
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        # фильтруем и отбрасываем дубликаты.
        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.filter(state=True)

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset)
        return Response(serializer.data)


class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class OrderView(APIView):
    """
    Класс для получения и размещения заказов пользователями
    Methods:
    - get: Retrieve the details of a specific order.
    - post: Create a new order.
    - put: Update the details of a specific order.
    - delete: Delete a specific order.

    Attributes:
    - None
    """

    # получить мои заказы
    def get(self, request, *args, **kwargs):
        """
               Получить подробную информацию о заказах пользователей.

               Args:
               - request (Request): The Django request object.

               Returns:
               - Response: The response containing the details of the order.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):
        """
               Оформите заказ и отправьте уведомление.

               Args:
               - request (Request): The Django request object.

               Returns:
               - JsonResponse: The response indicating the status of the operation and any errors.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        state='new')
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
                else:
                    if is_updated:
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class BasketView(APIView):
    """
    Класс для управления корзиной покупок пользователя.

    Methods:
    - get: Retrieve the items in the user's basket.
    - post: Add an item to the user's basket.
    - put: Update the quantity of an item in the user's basket.
    - delete: Remove an item from the user's basket.

    Attributes:
    - None
    """

    # получить корзину
    def get(self, request, *args, **kwargs):
        """
                Retrieve the items in the user's basket.

                Args:
                - request (Request): The Django request object.

                Returns:
                - Response: The response containing the items in the user's basket.
                """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    # редактировать корзину
    def post(self, request, *args, **kwargs):
        """
               Add an items to the user's basket.

               Args:
               - request (Request): The Django request object.

               Returns:
               - JsonResponse: The response indicating the status of the operation and any errors.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1

                    else:

                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

                return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        """
                Remove  items from the user's basket.

                Args:
                - request (Request): The Django request object.

                Returns:
                - JsonResponse: The response indicating the status of the operation and any errors.
                """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # добавить позиции в корзину
    def put(self, request, *args, **kwargs):
        """
               Update the items in the user's basket.

               Args:
               - request (Request): The Django request object.

               Returns:
               - JsonResponse: The response indicating the status of the operation and any errors.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками.
     Methods:
    - get: Retrieve the orders associated with the authenticated partner.

    Attributes:
    - None
    """

    def get(self, request, *args, **kwargs):
        """
               Retrieve the orders associated with the authenticated partner.

               Args:
               - request (Request): The Django request object.

               Returns:
               - Response: The response containing the orders associated with the partner.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
