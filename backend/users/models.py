from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(max_length=70, verbose_name='Имя')
    last_name = models.CharField(max_length=70, verbose_name='Фамилия')
    username = models.CharField(
        max_length=70, unique=True, verbose_name='Логин'
    )
    role = models.CharField(
        max_length=70,
        blank=True,
        verbose_name='Роль',
    )
    confirmation_code = models.TextField(
        unique=True, blank=True, null=True, verbose_name='Токен'
    )
    subscribers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscriptions',
        verbose_name='Подписчики'
    )

    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='customuser_groups',
        related_query_name='customuser',
        verbose_name='Группы',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_user_permissions',
        related_query_name='customuser',
        verbose_name='Доступы',
    )

    @property
    def is_subscribed(self):
        return self.subscribers.filter(id=self.request.user.id).exists()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return self.username
