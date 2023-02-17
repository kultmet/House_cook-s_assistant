from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
User = get_user_model()


class BaseIngredientWithUnits(models.Model):
    """Базавый ингредиент."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=225,
    )
    measurement_unit = models.CharField(
        verbose_name='Еденици измерения',
        max_length=30,
    )

    class Meta:
        verbose_name = 'Базовый ингредиент'
        verbose_name_plural = 'Базовые ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


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
    )
    cooking_time = models.PositiveIntegerField(
        default=1,
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1,
                'Ты хочешь чтоб это готовили? Добавь время приготовления!'
            ),
            MaxValueValidator(
                10080,
                'Ты предлагаешь готовить сюрстремминг? Ограничение - 10080.'
            )
        ]
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
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name

    def get_tag(self):
        return '\n'.join(
            [t.tag.name for t in TagRecipe.objects.filter(recipe=self)]
        )

    def get_ingeredient(self):
        return ', \n'.join([
            f'{i.base_ingredient.name} - '
            f'{i.amount} {i.base_ingredient.measurement_unit}'
            for i in IngredientRecipe.objects.filter(recipe=self)
        ])


class IngredientRecipe(models.Model):
    """
    Промежуточная таблица для привязки ингредиента к рецепту.
    Принимает колличество ингредиента для конкретного рецепта.
    """
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
    amount = models.PositiveIntegerField(
        verbose_name='Колличество',
        default=None,
        validators=[
            MinValueValidator(
                1,
                'Как ты можеш добавить игнредиент колличеством меньше 1?'
            ),
            MaxValueValidator(
                20000,
                'Ты предлагаешь готовить для ВиллаРриба и ВиллаБаджо сразу?'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['base_ingredient']

    def __str__(self):
        return (
            f'{self.base_ingredient.name}'
            f' - {self.amount} {self.base_ingredient.measurement_unit}'
        )

    def get_base_ingredient(self):
        """
        Этот метод для вывода в админку
        стокового отображения, Базового Ингредиента.
        """
        return self.base_ingredient

    def get_measurement_unit(self):
        """
        Этот метод для вывода в админку
        едениц измерение, Базового Ингредиента.
        """
        return self.base_ingredient.measurement_unit


class TagRecipe(models.Model):
    """Промежуточная таблица для привязки тэга к рецепту."""
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tag_for_recipe'
            ),
        ]
        ordering = ['-recipe__pub_date']
        verbose_name_plural = 'Связующая таблици для тегов'


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
        ordering = ['-recipe__pub_date']

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
        ordering = ['-recipe__pub_date']
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
