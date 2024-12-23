import requests
import json
import yaml
print("client")

# РЕГЕСТРИРУЕМ КЛИЕНТА.
# data = {
#     'first_name': 'Владимир',
#     'last_name': 'Иноземный',
#     'email': 'test@gmail.com',
#     'password': 'verystrongpassword789',
#     'company': 'Efes',
#     'position': 'manager'

# }
# response = requests.post("http://127.0.0.1:8000/api/v1/user/register", data=data)
# if response.status_code == 200:
#     print("Регистрация прошла успешно:", response.json())
# else:
#     print("Ошибка при регистрации:", response.status_code, response.text)
# ---------------------------------------------------------------------------------------------------------------------
# УДАЛЯЕМ КЛИЕНТА.
# response = requests.delete('http://localhost:8000/api/v1/user/delete/61/')
# print(response.status_code)
# ---------------------------------------------------------------------------------------------------------------------
# АВТОРИЗУЕМСЯ НА САЙТЕ.
# login_data = {
#     'email': 'test@gmail.com',  # kolyapolosin85@gmail.com
#     'password': 'verystrongpassword789'  # verystrongpassword123
# }
# response = requests.post('http://localhost:8000/api/v1/user/login/', data=login_data)
# if response.status_code == 200:
#     print("Успешная авторизация")
# else:
#     print(f"Ошибка авторизации: {response.status_code}")
# ---------------------------------------------------------------------------------------------------------------------
# AccountDetails GET
# response = requests.get("http://127.0.0.1:8000/api/v1/user/details",
#                         params={'email': 'kolyapolosin85@gmail.com',
#                                 'password': 'verystrongpassword123'})
# print(response.status_code)
# ---------------------------------------------------------------------------------------------------------------------
# AccountDetails POST
# data_new = {
#     'first_name': 'Владимир',
#     'last_name': 'Иноземный',
#     'email': 'test@gmail.com',  # kolyapolosin85@gmail.com
#     'password': 'verystrongpassword789',  # verystrongpassword123
#     'company': 'ООО Связной',
#     'position': 'Дворник',
#     'VariationUser': 'SHOP_REPRESENTATIVE',
#     # 'shop_id': '5'
# }
# headers = {'Content-Type': 'application/json'}
# response = requests.post("http://127.0.0.1:8000/api/v1/user/details", json=data_new, headers=headers)
# print(response.status_code)
# ---------------------------------------------------------------------------------------------------------------------
# Просмотр магазинов.
response = requests.get("http://127.0.0.1:8000/api/v1/shops")
print(response.status_code)
# ---------------------------------------------------------------------------------------------------------------------
# СОЗДАЕМ МАГАЗИН
# data = {
#     'name': 'Coca-Cola',
#     'url': 'http://127.0.0.1:8000/Coca-Cola',
#     'user': '61',
#     'state': 'True',
#     'email': 'kolyapolosin85@gmail.com',
#     'password': 'verystrongpassword123',
# }
# headers = {'Content-Type': 'application/json'}
# response = requests.post("http://127.0.0.1:8000/api/v1/shop/create", json=data, headers=headers)
# print('response.cookies')
# print(response.status_code)
# print(response.text)
# ---------------------------------------------------------------------------------------------------------------------
# ПОЛУЧАЕМ ИНФУ О МАГАЗИНЕ
# login_data = {
#     'email': 'test@gmail.com',  # kolyapolosin85@gmail.com
#     'password': 'verystrongpassword789'  # verystrongpassword123
# }
# response = requests.get("http://127.0.0.1:8000/api/v1/user/state")
# print(response.status_code)
# ---------------------------------------------------------------------------------------------------------------------
# ВЫВЕСТИ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ (для теста)
# response = requests.get('http://localhost:8000/api/v1/user/list/')
# if response.status_code == 200:
#     print("прошла успешно:", response.status_code)
# else:
#     print("Ошибка :", response.status_code)
# ---------------------------------------------------------------------------------------------------------------------
# ДОБАВЛЯЕМ ПРАЙС
# additional_data = {
#     # 'id': '61',
#     'first_name': 'Владимир',
#     'last_name': 'Иноземный',
#     'email': 'test@gmail.com',
#     'password': 'verystrongpassword789',
#     'VariationUser': 'SHOP_REPRESENTATIVE',
#     'url': 'https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml',
# }
#
# response = requests.post(
#     'http://localhost:8000/api/v1/price/update',
#     data=additional_data)
#
# if response.status_code == 200:
#     print("Все ок")
# else:
#     try:
#         print(f"Error loading data: {response.json()}")
#     except requests.exceptions.JSONDecodeError:
#         print("Не получилось не срослось, пацан к успеху шел.")
# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
# ПОДТВЕРЖДАЕМ


