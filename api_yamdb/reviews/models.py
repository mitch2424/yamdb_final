import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Category(models.Model):
    """Categories for titles model."""
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('Идентификатор', max_length=50, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель Genre."""
    name = models.CharField('Название', max_length=50)
    slug = models.SlugField('Идентификатор', unique=True, max_length=50)

    class Meta:
        ordering = ['id']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель Title."""
    name = models.CharField('Название', max_length=200)
    year = models.IntegerField(
        'Год',
        db_index=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(datetime.date.today().year)
        ]
    )
    description = models.TextField('Описание', blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанры',
        through='GenreTitle',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель Связь произведения с жанром ."""
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Связь произведения с жанром'
        verbose_name_plural = 'Связи произведения с жанром'


class Review(models.Model):
    """Модель Review."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель Comments."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
