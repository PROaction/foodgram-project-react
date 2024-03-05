from django.urls import path, include
from rest_framework import routers

from recipes.views import RecipeViewSet, TagViewSet, IngredientViewSet
from users.views import UserViewSet

app_name = 'recipes'


router = routers.SimpleRouter()
router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
