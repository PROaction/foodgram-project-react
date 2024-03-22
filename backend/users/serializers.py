from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import CustomUser


class UserListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return obj.subscribers.filter(id=user.id).exists()


class ReadUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        return ReadUserSerializer(instance).data


class PasswordChangeSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if not self.context['request'].user.check_password(
                data.get('current_password')):
            raise serializers.ValidationError(
                {'current_password': 'Неверный пароль'}
            )

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data.get('new_password'))
        user.save()
        return user


class SubscriberSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        from recipes.serializers import SimpleRecipeSerializer

        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]

        return SimpleRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return obj.subscribers.filter(id=request.user.id).exists()
