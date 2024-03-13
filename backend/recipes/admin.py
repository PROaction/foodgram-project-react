from django.contrib import admin

from recipes.models import Ingredient, Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'display_ingredients', 'display_tags', 'image', 'cooking_time',
        'text', 'author', 'created_at', 'updated_at', 'display_favorites'
    )
    search_fields = ('name',)
    list_filter = ('name', 'author__username', 'tags__name')

    def display_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    display_ingredients.short_description = 'Ингредиенты'

    def display_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = 'Тэги'

    def display_favorites(self, obj):
        return obj.is_favorited.count()

    display_favorites.short_description = 'Добавлено в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
