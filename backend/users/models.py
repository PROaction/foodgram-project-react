from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


# USER = 'user'
# ADMIN = 'admin'
# MODERATOR = 'moderator'
#
# ROLES = (
#     (USER, 'User'),
#     (ADMIN, 'Moderator'),
#     (MODERATOR, 'Admin'),
# )


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70)
    username = models.CharField(max_length=70, unique=True)
    role = models.CharField(
        max_length=70,
        # choices=ROLES,
        # default=USER,
        blank=True,
    )
    confirmation_code = models.TextField(
        unique=True,
        blank=True,
        null=True,
    )
    subscribers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscriptions'
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_user_permissions",
        related_query_name="customuser",
    )

    # @property
    # def is_admin(self):
    #     return self.role == ADMIN or self.is_superuser
    #
    # @property
    # def is_moderator(self):
    #     return self.role == MODERATOR or self.is_admin

    @property
    def is_subscribed(self):
        return self.subscribers.filter(id=self.request.user.id).exists()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
