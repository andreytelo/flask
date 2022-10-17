import requests

# Созданние пользователя
response1 = requests.post('http://127.0.0.1:5000/user',
                          json={'username': 'final_test_user', 'password': '1234'}, )

print(response1.status_code)
print(response1.json())

# Создание статьи
response2 = requests.post('http://127.0.0.1:5000/advertisement',
                          json={'title': 'final_test_title', 'description': 'some_description', 'user_id': 75}, )

print(response2.status_code)
print(response2.json())

# Получение инфы о пользователе
response3 = requests.get('http://127.0.0.1:5000/user/75', )

print(response3.status_code)
print(response3.json())

# Получение инфы о статье
response4 = requests.get('http://127.0.0.1:5000/advertisement/53')

print(response4.status_code)
print(response4.json())

# Изменение имени пользователя(get-запрос для проверки изменения)
response5 = requests.patch('http://127.0.0.1:5000/user/75', json={'username': 'final_user'})

print(response5.status_code)
print(response5.json())

response3 = requests.get('http://127.0.0.1:5000/user/75', )
print(response3.status_code)
print(response3.json())

# Изменение статьи(get-запрос для проверки изменения)
response6 = requests.patch('http://127.0.0.1:5000/advertisement/53',
                           json={'title': 'final_title', 'description': 'another_description'})

print(response6.status_code)
print(response6.json())

response4 = requests.get('http://127.0.0.1:5000/advertisement/53')

print(response4.status_code)
print(response4.json())

# Удаление пользователя и проверка
response7 = requests.delete('http://127.0.0.1:5000/user/75', )

print(response7.status_code)
print(response7.json())

response3 = requests.get('http://127.0.0.1:5000/user/75', )

print(response3.status_code)
print(response3.json())

# Удаление статьи и проверка
response8 = requests.delete('http://127.0.0.1:5000/advertisement/53')

print(response8.status_code)
print(response8.json())

response4 = requests.get('http://127.0.0.1:5000/advertisement/53')

print(response4.status_code)
print(response4.json())
