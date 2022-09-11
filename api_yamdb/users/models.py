from django.contrib.auth.models import AbstractUser
from django.db import models

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
    (MODERATOR, 'Модератор'),
)


class User(AbstractUser):
    """User model customization class."""
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    bio = models.TextField('Биография', blank=True, null=True)
    role = models.CharField('Роль пользователя',
                            max_length=max([len(role[0]) for role in ROLES]),
                            choices=ROLES,
                            default=USER)
    password = models.CharField('Пароль',
                                max_length=128,
                                blank=True,
                                null=True,
                                default='')

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
