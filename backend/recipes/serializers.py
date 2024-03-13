import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
import six

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.serializers import UserListSerializer


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
            complete_file_name = "%s.%s" % (
                file_name,
                file_extension,
            )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.DecimalField(
        max_digits=5, decimal_places=2, source='quantity'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Количество ингредиента должно быть больше 0."
            )
        return value


class IngredientReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
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
    ingredients = RecipeIngredientReadSerializer(
        many=True, read_only=True, source='recipeingredient_set'
    )
    tags = TagReadSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'name', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'image', 'cooking_time', 'text'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return obj.is_favorited.filter(id=user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return obj.is_in_shopping_cart.filter(id=user.id).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True, required=True)
    tags = serializers.ListField(child=serializers.IntegerField())
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )

    class Meta:
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name', 'image', 'text',
            'cooking_time'
        )
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
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(
                "Поле 'ingredients' должно быть заполнено."
            )
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                "Поле 'tags' должно быть заполнено."
            )

        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.recipeingredient_set.all().delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
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

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                "Поле 'ingredients' должно быть заполнено."
            )

        if len(ingredients) == 0:
            raise serializers.ValidationError(
                "Список ингредиентов не может быть пустым."
            )

        ingredient_ids = [ingredient['id'].id for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )
        return ingredients

    def validate_tags(self, tag_ids):
        if len(tag_ids) == 0:
            raise serializers.ValidationError(
                "Список тэгов не должен быть пустым."
            )

        for tag_id in tag_ids:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    f"Тег с id {tag_id} не существует."
                )

        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError("Тэги не должны повторяться.")

        return tag_ids

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError("Значение должно быть больше 0.")
        return value


class SimpleRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
