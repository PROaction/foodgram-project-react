from django.contrib.auth import get_user_model
from django.db import models

from foodgram_backend import settings


User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.ManyToManyField(
        'Ingredient', through='RecipeIngredient'
    )
    tags = models.ManyToManyField('Tag', through='RecipeTag')
    is_favorited = models.ManyToManyField(
        User, related_name='favorited_recipes'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User, related_name='recipes_in_cart'
    )
    image = models.ImageField(upload_to='recipes/images/')
    cooking_time = models.IntegerField()
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Ingredient(models.Model):
    name = models.CharField(max_length=settings.CHAR_NAME)
    measurement_unit = models.CharField(max_length=settings.CHAR_NAME)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)


class Tag(models.Model):
    name = models.CharField(max_length=settings.CHAR_NAME)
    color = models.CharField(max_length=settings.CHAR_NAME)
    slug = models.SlugField(max_length=settings.CHAR_NAME)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
