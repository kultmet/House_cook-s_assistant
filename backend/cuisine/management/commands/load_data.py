import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

# from redis import Redis
# print(settings.BASE_DIR)
from cuisine.models import BaseIngredientWithUnits as Ingredient

# # redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)

class Command(BaseCommand):
    """Команда для загрузки csv файлов в базу данных:
     python manage.py fill_database."""
    
    help = 'Загрузка информации из csv файлов в базу данных'


    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'ingredients.csv'),
                    'rt', encoding='utf-8') as csv_file:
            render = csv.reader(csv_file)
            
            for i in render:
                print(i)
                ingredient = Ingredient()
                ingredient.name = i[0]
                ingredient.measurement_unit = i[1]
                ingredient.save()
        print('finished')
