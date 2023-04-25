from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from . import validators
from api.storage import UserAvatarStorage

# Create your models here.

class UserManager(BaseUserManager):
    """
    Менеджер экземплятров модели `User` без поля `username`
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создаёт и сохраняет экземпляр модели `User`

        Paramaters
        ----------
        email : str
            Электронная почта
        password : str
            Пароль

        Returns
        -------
        user : User
            Экземпляр модели пользователя
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        print("manager message - user saved:", str(user))
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Создаёт обычного пользователя User по `email`, `password`

        Paramaters
        ----------
        email : str
            Электронная почта
        password : str
            Пароль

        Returns
        -------
        user : User
            Экземпляр модели пользователя
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Создаёт суперпользователя User по `email`, `password`

        Paramaters
        ----------
        email : str
            Электронная почта
        password : str
            Пароль

        Returns
        -------
        user : User
            Экземпляр модели пользователя
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True)
    avatar = models.ImageField(blank=True, null=True, max_length=400, storage=UserAvatarStorage())
    phone = models.CharField(max_length=14, blank=True, null=True, validators=[validators.isPhoneNumber])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return f'{self.email}'
    
    class Meta:
        ordering = ('phone',)
    
class Organization(models.Model):

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    users = models.ManyToManyField(User, blank=True, default=[])

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)