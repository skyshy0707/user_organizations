import base64
import os
import random
import re
import string

from django.core.files import File
from PIL import Image, UnidentifiedImageError
from resizeimage import resizeimage
from rest_framework import serializers

from user_organizations.settings import BASE_DIR
from . import models

MIMES_IMAGE = {
    'BMP': 'image/bmp', 'DIB': 'image/bmp', 'GIF': 'image/gif', 
    'TIFF': 'image/tiff', 'JPEG': 'image/jpeg', 'JPG': 'image/jpeg', 
    'PPM': 'image/x-portable-anymap', 'PNG': 'image/png', 'PCX': 'image/x-pcx', 
    'EPS': 'application/postscript', 'JPEG2000': 'image/jp2', 
    'ICNS': 'image/icns', 'ICO': 'image/x-icon', 'MPEG': 'video/mpeg', 
    'MPO': 'image/mpo', 'PALM': 'image/palm', 'PDF': 'application/pdf', 
    'PSD': 'image/vnd.adobe.photoshop', 'SGI': 'image/sgi', 'TGA': 'image/x-tga', 
    'WEBP': 'image/webp', 'XBM': 'image/xbm', 'XPM': 'image/xpm'
}
NAME_LENGTH = 20
REQUIRED_HEIGHT = 200
REQUIRED_WIDTH = 200
USER_AVATARS_PATH = BASE_DIR.joinpath('api//user_avatars')

class AvatarField(serializers.ImageField):
    """
    Класс сериализатора файлового поля `avatar`
    отличается реализацией метода `to_internal_value` 
    в том, что после преобразования значения в тип python 
    происходит освобождение файла от процесса, который 
    открывает его содержимое.

    !!
    Предназначен для использования в сериализаторе 
    `UserSerializer`
    !!
    """

    def to_internal_value(self, data):
        """
        Данный метод переоперделён для перевода сериализованного 
        значения поля `avatar` в тип python.

        После преобразования значения в тип python метод закрывает файл, 
        так как операции, связанные с его загрузкой уже были произведены в 
        методе `api.UserSerializer.to_internal_value`

        Parameters
        ----------
        data : django.core.files.Files
            Открытый файловый поток, содержащий контент поля `avatar` 
            модели `api.User`

        Returns
        -------
        value : io.BufferedReader
            Закрытый файловый поток, содержащий контент поля `avatar` 
            модели `api.User`
        """
        file_object = super(serializers.ImageField, self).to_internal_value(data)
        django_field = self._DjangoImageField()
        django_field.error_messages = self.error_messages
        value = django_field.clean(file_object)
        file_object.close()
        return value
    
class StringRelatedSerializer(serializers.StringRelatedField):
    """
    Класс используется для сериализации и десериализации 
    значений первичных ключей. Отличается реализованным методом
    `to_internal_value`
    """

    def to_internal_value(self, data):
        """
        Производит десериализацию набора первичных ключей, 
        представленных списком или отдельного такого ключа
        """
        return data

class UserSerializer(serializers.ModelSerializer):
    """
    Класс используется для десериализации данных модели 
    `User` на запись.

    Отличается реализацией метода `to_internal_value` в том, 
    что в нём производится загрузка файла для поля `avatar`
    в директорию пользователя /api/user_avatars/<User.email>
    """

    organization_set = StringRelatedSerializer(many=True, required=False)
    avatar = AvatarField(use_url=True, required=False)

    class Meta:
        model = models.User
        fields = ('id', 'email', 'phone', 'first_name', 'last_name', 'avatar', 'organization_set')

    def to_internal_value(self, data):
        """
        Устаналивает значения полей `avatar`, `email` для передачи 
        на проверку сериализатором. Производит загрузку файла
        для поля `avatar`, предваритеольно преобразовывая 
        последовательность байтов к типу django.core.files.Files

        Parameters
        ----------
        data : dict
            Данные json, полученные от клиента
        
        Returns
        -------
        ret : collections.OrderedDict
            Десериализованные данные для проверки
        """
        avatar = data.get("avatar")
        filename = avatar.get("filename") if avatar else ''
        file_string = avatar.get("file_bytes") if avatar else ''
        basename, extension = os.path.splitext(filename)

        if self.instance:
            email = data.get('email', self.instance.email)
            data['email'] = email

        #Генерирование имени файла, если имя не содержит символы [a-zA-Z0-9]:
        if avatar and extension[1:].upper() in MIMES_IMAGE:
            if not re.fullmatch(r'([a-zA-Z0-9])+', basename) or not basename:
                filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=NAME_LENGTH)  + [extension])

            #Установка пути к файлу аватара:
            THIS_USER_AVATAR_PATH = USER_AVATARS_PATH.joinpath(f"{email}")

            #При загрузке нового аватара производится очистка папки с файлами 
            #больше неактуальных аватаров пользователя:
            if THIS_USER_AVATAR_PATH.exists() and file_string:
                user_avatar_files = os.listdir(THIS_USER_AVATAR_PATH)
                for file_ in user_avatar_files:
                    _, extension = os.path.splitext(file_)

                    if extension[1:].upper() in MIMES_IMAGE:
                        os.remove(THIS_USER_AVATAR_PATH.joinpath(file_))
            try:
                THIS_USER_AVATAR_PATH.mkdir(mode=777)
            except FileExistsError:
                pass
            file_path = THIS_USER_AVATAR_PATH.joinpath(f'{filename}')

        
            with open(file_path, 'wb') as f:
                try:
                    writeble_bytes = bytes(file_string[2:-1], 'utf-8')
                    f.write(base64.b64decode(writeble_bytes))
                except TypeError:
                    pass

            with open(file_path, 'r+b') as f:
                try:
                    with Image.open(f) as image:
                        height, width = image.size     
                        if height > REQUIRED_HEIGHT or width > REQUIRED_WIDTH:
                            resized = resizeimage.resize_cover(image, [REQUIRED_HEIGHT, REQUIRED_WIDTH])
                            resized.save(file_path, image.format)
                except UnidentifiedImageError:
                    pass
            desired_file = open(file_path, 'rb')
            data['avatar'] = File(desired_file)

        return super(UserSerializer, self).to_internal_value(data)

class OrganizationSerializer(serializers.ModelSerializer):
    """
    Класс используется для десериализации данных модели 
    `Organization` на запись
    """
    users = StringRelatedSerializer(many=True, required=False)

    class Meta:
        model = models.Organization
        fields = '__all__'

    def to_internal_value(self, data):
        """
        Устаналивает значения поля `name` для передачи на проверку 
        сериализатором

        Parameters
        ----------
        data : dict
            Данные json, полученные от клиента
        
        Returns
        -------
        ret : collections.OrderedDict
            Десериализованные данные для проверки
        """
        if self.instance:
            name = self.instance.name
            data['name'] = data.get('name', name)
        return super(OrganizationSerializer, self).to_internal_value(data)

class UserSerializerOnlyRead(serializers.ModelSerializer):
    """
    Класс используется для сериализации данных модели 
    `User` на чтение
    """
    organization_set = OrganizationSerializer(many=True, required=False)
    avatar = serializers.ImageField(use_url=True)

    class Meta:
        model = models.User
        fields = ('id', 'email', 'phone', 'first_name', 'last_name', 'avatar', 'organization_set')

class OrganizationOnlyRead(serializers.ModelSerializer):
    """
    Класс используется для сериализации данных модели 
    `Organization` на чтение
    """
    users = UserSerializer(many=True, required=False)

    class Meta:
        model = models.Organization
        fields = '__all__'