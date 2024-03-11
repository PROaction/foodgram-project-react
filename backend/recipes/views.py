import os
import tempfile

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from recipes.paginators import StandardResultsSetPagination, Pagination
from recipes.permissions import IsOwnerOrReadOnly
from recipes.serializers import IngredientReadSerializer, AddRecipeSerializer, TagReadSerializer, \
    RecipeReadSerializer, RecipeWriteSerializer
from fpdf import FPDF
from tempfile import NamedTemporaryFile
from rest_framework import serializers


class PDF(FPDF):
    def header(self):
        self.set_font('FreeSans', '', 12)
        self.cell(0, 10, 'Список покупок', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('FreeSans', '', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('FreeSans', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def print_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)


class RecipeViewSet(ModelViewSet):
    # permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
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
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart', None)

        if author_id is not None:
            queryset = queryset.filter(author__id=author_id)
        if tags is not None and len(tags) > 0:
            queryset = queryset.filter(tags__slug__in=tags)

        if is_favorited is not None:
            if is_favorited in ['0', '1']:
                flag = True if is_favorited == '1' else False
                queryset = queryset.filter(is_favorited=flag)
            else:
                raise serializers.ValidationError({"is_favorited": "This field can only be 0 or 1."})

        if is_in_shopping_cart is not None:
            if is_in_shopping_cart in ['0', '1']:
                flag = True if is_in_shopping_cart == '1' else False
                queryset = queryset.filter(is_in_shopping_cart=flag)
            else:
                raise serializers.ValidationError({"is_in_shopping_cart": "This field can only be 0 or 1."})

        return queryset

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'

        pdf = PDF()
        pdf.add_font('FreeSans', '', 'static/freesans.ttf', uni=True)

        recipes_in_cart = Recipe.objects.filter(is_in_shopping_cart=True)
        ingredients = RecipeIngredient.objects.filter(recipe__in=recipes_in_cart)
        ingredients = ingredients.values('ingredient__name', 'ingredient__measurement_unit'
                                         ).annotate(total_quantity=Sum('quantity'))
        text = ''
        for ingredient in ingredients:
            text += '\n' + (f'{ingredient["ingredient__name"]} '
                            f'({ingredient["ingredient__measurement_unit"]}) — '
                            f'{ingredient["total_quantity"]}')
        pdf.print_chapter('Список покупок:', text)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
            pdf.output(temp.name, 'F')
            temp.seek(0)
            response.write(temp.read())
            temp.close()  # close the file before deleting it

        os.unlink(temp.name)
        return response

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, *args, **kwargs):
        # recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        try:
            recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"detail": "Рецепт не найден"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if recipe.is_in_shopping_cart:
                return Response({"detail": "Рецепт уже в корзине покупок"}, status=status.HTTP_400_BAD_REQUEST)
            recipe.is_in_shopping_cart = True
            recipe.save()

            serializer = AddRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not recipe.is_in_shopping_cart:
                return Response({"detail": "Рецепт отсутствует в корзине покупок"}, status=status.HTTP_400_BAD_REQUEST)
            recipe.is_in_shopping_cart = False
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, *args, **kwargs):
        # recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        try:
            recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"detail": "Рецепт не найден"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if recipe.is_favorited:
                return Response({"detail": "Рецепт уже в избранном"}, status=status.HTTP_400_BAD_REQUEST)
            recipe.is_favorited = True
            recipe.save()

            serializer = AddRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not recipe.is_favorited:
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
