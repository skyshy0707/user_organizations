**Информация**

Проект разработан на версии Django 3.1.7, Django Rest Framework 3.12.4.

Директория загрузки и хранения аватара пользователя: `api/user_avatars/<email пользователя>` 

**Запуск проекта из терминала**

1. Перейдите в корень проекта.

2. Установите виртуальную среду:

```
python -m venv venv
```

3. Активируйте виртуальную среду, согласно инструкциям используемой системы.

4. Установите зависимости:

```
pip install -r requirements.txt
```

5. Примените миграции:

```
python manage.py makemigrations
python manage.py migrate
```

6. Запустите сервер:

```
python manage.py runserver <НОМЕР_ПОРТА>
```

**Запуск тестов**

```
cd to/root/project
```

```
python manage.py test
```

В `api/TEST_AVATARS` находятся примеры изображений аватаров, которые использовались для тестирования.