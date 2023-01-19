from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Recipe(models.Model):
    """Модель для Рецепта."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    tag = models.ManyToManyField(
        'Tag',
        verbose_name='теги',
        related_name='recipes',
    )
    ingredient = models.ManyToManyField(
        'Ingredient',
        verbose_name='ingredient',
        related_name='recipes'
    )
    coockung_time = models.IntegerField(
        default=1,
        verbose_name='Время приготовления'
    )
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Загрузить фото')
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


class Tag(models.Model):
    """Модель для Тегов."""
    name = models.CharField(
        max_length=30,
        verbose_name='Название Тега'
    )
    color = models.CharField(
        max_length=15,
        verbose_name='Цвет Тега'
    )
    slug = models.SlugField(
        max_length=45,
        verbose_name='Slug'
    )


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=100
    )
    amount = models.IntegerField(
        verbose_name='Колличество',
        default=None
    )
    measurement_unit = models.CharField(
        verbose_name='Еденици измерения',
        max_length=30
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
        related_name='orders'
    )