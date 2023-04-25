import base64
import configparser
import os

from rest_framework import status
from rest_framework.test import APITestCase
from . import models
from user_organizations.settings import BASE_DIR

config = configparser.ConfigParser()
config.read('./config.ini')

API_URL = f"{config['site']['domain']}/api"
EMAIL_NAME_LENGTH = 10
TEST_AVATAR_PATH = BASE_DIR.joinpath("api//TEST_AVATARS")

# Create your tests here.
class UserOrganizationsAPITestCase(APITestCase):

    def setUp(self):
        #Создаём пользователей и организации до двух страниц:
        user = models.User.objects.create(email="someone1@yandex.ru")
        user2 = models.User.objects.create(email="someone2@yandex.ru")
        user3 = models.User.objects.create(email="someone3@yandex.ru")
        user4 = models.User.objects.create(email="someone4@yandex.ru")
        user5 = models.User.objects.create(email="someone5@yandex.ru")
        user6 = models.User.objects.create(email="someone6@yandex.ru")
        user7 = models.User.objects.create(email="someone7@yandex.ru")
        user8 = models.User.objects.create(email="someone8@yandex.ru")
        user9 = models.User.objects.create(email="someone9@yandex.ru")
        user10 = models.User.objects.create(email="someone10@yandex.ru")
        user11 = models.User.objects.create(email="someone11@yandex.ru")
        user12 = models.User.objects.create(email="someone12@yandex.ru")
        organization = models.Organization.objects.create(name="ГК Титан")
        organization2 = models.Organization.objects.create(name="Уфаоргсинтез")
        organization3 = models.Organization.objects.create(name="ОДК-УМПО")
        organization4 = models.Organization.objects.create(name="НПП Буринтех")
        organization5 = models.Organization.objects.create(name="Сбербанк")
        organization6 = models.Organization.objects.create(name="ООО Таливенда")
        organization7 = models.Organization.objects.create(name="ПО Авви")
        organization8 = models.Organization.objects.create(name="ПО Технотех")
        organization9 = models.Organization.objects.create(name="МКС")
        organization10 = models.Organization.objects.create(name="Ажурсталь")
        organization11 = models.Organization.objects.create(name="Белоярская АЭС")
        #Устанавливаем организации и пароль для тестового пользователя:
        user.organization_set.add(organization, organization2)
        user.set_password("qwerty1234")
        user.save()
        #Настраиваем аутентификацию по JWT для тестов:
        basic_auth_data = { "email": "someone1@yandex.ru", "password": "qwerty1234" }
        response = self.client.post(f'{API_URL}/token/', basic_auth_data, format='json')
        access_token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_registration(self):
        filestream = open(TEST_AVATAR_PATH.joinpath("av-to-change.png"), 'rb')
        body = {
            "email": f'someone13@yandex.ru',
            "password": "qwerty1234",
            "password2": "qwerty1234",
            "first_name": "Andrey",
            "last_name": "Minnullin",
            "avatar": {
                'file_bytes': str(base64.b64encode(filestream.read())),
                'filename': os.path.basename(filestream.name)
            }
        }
        response = self.client.post(f"{API_URL}/signup/", body, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_organization_create(self):
        body = {
            "name": "ФГУП НИИ Радиосвязи", 
            "description": "Исследование и разработка радиоэлектроники, прибостроение"
        }
        url = f"{API_URL}/organization/create/"
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_organizations_get(self):
        url = f"{API_URL}/organizations/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["page_links"]), 2)

    def test_user_get(self):
        url = f"{API_URL}/user/?pk=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_edit(self):
        filestream = open(TEST_AVATAR_PATH.joinpath("av-to-change.png"), 'rb')
        stream = filestream.read()
        body = { 
            "avatar": {
                'file_bytes': str(base64.b64encode(stream)),
                'filename': os.path.basename(filestream.name)
            }
        }
        url = f"{API_URL}/user/edit/?pk=1"
        response = self.client.put(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_users_get(self):
        url = f"{API_URL}/users/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["page_links"]), 2)