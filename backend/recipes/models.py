from django.contrib.auth import get_user_model
from django.db import models

from foodgram_backend import settings

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(max_length=settings.CHAR_NAME)
    ingredients = models.ManyToManyField('Ingredient', through='RecipeIngredient')
    tags = models.ManyToManyField('Tag', through='RecipeTag')
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    image = models.ImageField(upload_to='recipes/images/')
    cooking_time = models.IntegerField()
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=settings.CHAR_NAME)
    measurement_unit = models.CharField(max_length=settings.CHAR_NAME)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)


class Tag(models.Model):
    name = models.CharField(max_length=settings.CHAR_NAME)
    color = models.CharField(max_length=settings.CHAR_NAME)
    slug = models.SlugField(max_length=settings.CHAR_NAME)


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
