import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from cuisine.models import BaseIngredientWithUnits as Ingredient
from cuisine.models import Tag

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
        tags_parameters = (
            ('Завтрак', '#FF7F50', 'breakfast'),
            ('Обед', '#3CB371', 'lunch'),
            ('Ужин', '#8A2BE2', 'dinner'),
        )
        for tag_parameters in tags_parameters:
            print(tag_parameters)
            tag = Tag()
            tag.name = tag_parameters[0]
            tag.color = tag_parameters[1]
            tag.slug = tag_parameters[2]
            tag.save()
            print(f'Тэг {tag_parameters[0]} сохранен.')
        print('finished')
