from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from recipes.paginators import StandardResultsSetPagination
from recipes.permissions import IsOwnerOrReadOnly
from recipes.serializers import IngredientReadSerializer, AddRecipeSerializer, TagReadSerializer, \
    RecipeReadSerializer, RecipeWriteSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    # permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'

        doc = SimpleDocTemplate(response)
        styles = getSampleStyleSheet()
        story = []

        recipes_in_cart = Recipe.objects.filter(is_in_shopping_cart=True)
        ingredients = RecipeIngredient.objects.filter(recipe__in=recipes_in_cart)
        ingredients = ingredients.values('ingredient__name', 'ingredient__measurement_unit'
                                         ).annotate(total_quantity=Sum('quantity'))
        text = ''
        for ingredient in ingredients:
            text += '\n' + (f'{ingredient["ingredient__name"]} '
                            f'({ingredient["ingredient__measurement_unit"]}) — '
                            f'{ingredient["total_quantity"]}')
        story.append(Paragraph(text, styles['Normal']))

        doc.build(story)
        return response

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])

        if request.method == 'POST':
            if recipe.is_in_shopping_cart:
                return Response({"detail": "Рецепт уже в корзине покупок"}, status=status.HTTP_400_BAD_REQUEST)
            recipe.is_in_shopping_cart = True
            recipe.save()

            serializer = AddRecipeSerializer(recipe)
            return Response(serializer.data)
        elif request.method == 'DELETE':
            if not recipe.is_in_shopping_cart:
                return Response({"detail": "Рецепт отсутствует в корзине покупок"}, status=status.HTTP_400_BAD_REQUEST)
            recipe.is_in_shopping_cart = False
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])

        if request.method == 'POST':
            if recipe.is_in_shopping_cart:
                return Response({"detail": "Рецепт уже в избранном"}, status=status.HTTP_400_BAD_REQUEST)
            recipe.is_favorited = True
            recipe.save()

            serializer = AddRecipeSerializer(recipe)
            return Response(serializer.data)
        elif request.method == 'DELETE':
            if not recipe.is_in_shopping_cart:
                return Response({"detail": "Рецепт отсутствует в избранном"}, status=status.HTTP_400_BAD_REQUEST)
            recipe.is_favorited = False
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagReadSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientReadSerializer
