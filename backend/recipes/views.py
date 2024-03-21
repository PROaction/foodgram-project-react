import os
import tempfile

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.filters import IngredientFilter
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipes.paginators import Pagination
from recipes.permissions import IsOwnerOrReadOnly
from recipes.serializers import (
    IngredientReadSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SimpleRecipeSerializer,
    TagReadSerializer,
)
from recipes.utils import PDF


class RecipeViewSet(ModelViewSet):
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        author_id = self.request.query_params.get('author', None)
        tags = self.request.query_params.getlist('tags', None)
        is_favorited = self.request.query_params.get('is_favorited', None)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None
        )

        if is_favorited not in ['0', '1']:
            raise serializers.ValidationError(
                {'is_favorited': 'Это поле может принять только 0 или 1.'}
            )
        if is_in_shopping_cart not in ['0', '1']:
            raise serializers.ValidationError(
                {
                    'is_in_shopping_cart':
                        'Это поле может принять только 0 или 1.'
                }
            )

        if author_id is not None:
            queryset = queryset.filter(author__id=author_id)
        if tags is not None and len(tags) > 0:
            queryset = queryset.filter(tags__slug__in=tags)

        if is_favorited is not None:
            if is_favorited in ['0', '1']:
                flag = True if is_favorited == '1' else False
                queryset = queryset.filter(is_favorited=flag)

        if is_in_shopping_cart is not None:
            if is_in_shopping_cart in ['0', '1']:
                flag = True if is_in_shopping_cart == '1' else False
                queryset = queryset.filter(is_in_shopping_cart=flag)

        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; '
            'filename="shopping_cart.pdf"'
        )

        pdf = PDF()
        pdf.add_font('FreeSans', '', 'static/freesans.ttf', uni=True)

        recipes_in_cart = Recipe.objects.filter(is_in_shopping_cart=True)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_in_cart
        )
        ingredients = ingredients.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_quantity=Sum('quantity'))
        text = ''
        for ingredient in ingredients:
            text += '\n' + (
                f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) — '
                f'{ingredient["total_quantity"]}'
            )
        pdf.print_chapter('Список покупок:', text)

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            pdf.output(temp.name, 'F')
            temp.seek(0)
            response.write(temp.read())
            temp.close()

        os.unlink(temp.name)
        return response

    @action(detail=True, methods=['post', 'delete'])
    @permission_classes([IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(
                {'detail': 'Рецепт не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if request.user in recipe.is_in_shopping_cart.all():
                return Response(
                    {'detail': 'Рецепт уже в корзине покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe.is_in_shopping_cart.add(request.user)
            serializer = SimpleRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if request.user not in recipe.is_in_shopping_cart.all():
                return Response(
                    {'detail': 'Рецепт отсутствует в корзине покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe.is_in_shopping_cart.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    @permission_classes([IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        try:
            recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(
                {'detail': 'Рецепт не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if request.user in recipe.is_favorited.all():
                return Response(
                    {'detail': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe.is_favorited.add(request.user)

            serializer = SimpleRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if request.user not in recipe.is_favorited.all():
                return Response(
                    {'detail': 'Рецепт отсутствует в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe.is_favorited.remove(request.user)

            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagReadSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientReadSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
