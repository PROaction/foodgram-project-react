from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import Recipe, Ingredient, RecipeIngredient, Tag, RecipeTag
from users.serializers import UserListSerializer

from django.core.files.base import ContentFile
import base64
import six
import uuid
import imghdr


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.DecimalField(max_digits=5, decimal_places=2, source='quantity')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class IngredientReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    amount = serializers.IntegerField(source='quantity', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagWriteSerializer(serializers.ListSerializer):
    child = serializers.IntegerField()

    # class Meta:
    #     model = Tag
    #     fields = ('id',)


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserListSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(many=True, read_only=True, source='recipeingredient_set')
    tags = TagReadSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'image', 'cooking_time', 'text')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.ListField(child=serializers.IntegerField())
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        fields = ('id', 'ingredients', 'tags', 'image', 'name',
                  'image', 'text', 'cooking_time')
        model = Recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                quantity=ingredient['quantity'],
            )

        for tag in tags:
            current_tag = Tag.objects.get(id=tag)
            RecipeTag.objects.create(
                recipe=recipe,
                tag=current_tag,
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.recipeingredient_set.all().delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(recipe=instance,
                                            ingredient=ingredient['id'],
                                            quantity=ingredient['quantity'],
                                            )

        instance.tags.clear()
        for tag_id in tags_data:
            tag = Tag.objects.get(id=tag_id)
            instance.tags.add(tag)

        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance, context=self.context)
        return serializer.data


class AddRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
