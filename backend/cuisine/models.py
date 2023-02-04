from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseIngredientWithUnits(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=50,
        blank=True,# убрать
        null=True# убрать
    )
    measurement_unit = models.CharField(
        verbose_name='Еденици измерения',
        max_length=30,
        blank=True,# убрать
        null=True# убрать
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Базовый ингредиент'
        verbose_name_plural = 'Базовые ингредиенты'


class Tag(models.Model):
    """Модель для Тегов."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=30,
        verbose_name='Название Тега',
        unique=True
    )
    color = models.CharField(
        max_length=15,
        verbose_name='Цвет Тега',
        unique=True
        
    )
    slug = models.SlugField(
        max_length=45,
        verbose_name='Slug',
        unique=True
    )
    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
    
    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель для Рецепта."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='теги',
        related_name='recipes',
        through='TagRecipe'
    )
    ingredients = models.ManyToManyField(
        BaseIngredientWithUnits,
        verbose_name='ingredient',
        related_name='recipes',
        through='IngredientRecipe'
        # blank=True,# убрать
        # null=True
    )
    cooking_time = models.PositiveIntegerField(
        default=1,
        verbose_name='Время приготовления'
    )
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        verbose_name='Загрузить фото',
        upload_to='recipes/'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    def __str__(self):
        return self.name
    
    def get_tag(self):
        return '\n'.join([t.tag.name for t in TagRecipe.objects.filter(recipe=self)])
    
    def get_ingeredient(self):
        return ', \n'.join([f'{i.base_ingredient.name} - {i.amount} {i.base_ingredient.measurement_unit}' for i in IngredientRecipe.objects.filter(recipe=self)])#{i.amount} 


class IngredientRecipe(models.Model):
    base_ingredient = models.ForeignKey(
        BaseIngredientWithUnits,
        on_delete=models.CASCADE,
        related_name='ingredientrecipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientrecipe'
    )
    amount = models.IntegerField(
        verbose_name='Колличество',
        default=None
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.base_ingredient.name} - {self.amount} {self.base_ingredient.measurement_unit}'
    
    def get_name(self):
        return self.base_ingredient.name

    def get_base_ingredient(self):
        return self.base_ingredient
    
    def get_id(self):
        return self.base_ingredient.id

    def get_measurement_unit(self):
        return self.base_ingredient.measurement_unit


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tagrecipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tagrecipe'
    )
    

class Favorite(models.Model):
    """Модель для Избранного."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favorites',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        ]

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Order(models.Model):
    """Модель для Покупки."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='orders',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='orders',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_order'
            ),
        ]
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
