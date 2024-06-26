import os
import sys
import json
from django.conf import settings


sys.path.append('/app')

os.environ['DJANGO_SETTINGS_MODULE'] = 'foodgram_backend.settings'


import django
django.setup()

from recipes.models import Ingredient, Tag


def load_data():
    with open('/data/ingredients.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        Ingredient.objects.create(
            name=item['name'],
            measurement_unit=item['measurement_unit']
        )

    with open('/data/tags.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        Tag.objects.create(
            name=item['name'],
            color=item['color'],
            slug=item['slug'],
        )


load_data()
