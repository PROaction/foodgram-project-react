from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram_backend.settings import MAX_VALUE, MIN_VALUE


User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    ingredients = models.ManyToManyField(
        'Ingredient', through='RecipeIngredient', verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        'Tag', through='RecipeTag', verbose_name='Тeги'
    )
    is_favorited = models.ManyToManyField(
        User,
        related_name='favorited_recipes',
        verbose_name='Добавлено в избранное'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User, related_name='recipes_in_cart', verbose_name='В корзине'
    )
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='Изображение'
    )
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        ],
        verbose_name='Время приготовления',
    )
    text = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=settings.CHAR_NAME, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=settings.CHAR_NAME, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    quantity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        ],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Tag(models.Model):
    name = models.CharField(
        max_length=settings.CHAR_NAME, verbose_name='Название'
    )
    color = models.CharField(
        max_length=settings.CHAR_NAME, verbose_name='Цвет'
    )
    slug = models.SlugField(max_length=settings.CHAR_NAME, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        'Tag', on_delete=models.CASCADE, verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        ordering = ('tag',)

    def __str__(self):
        return f'{self.recipe} - {self.tag}'
