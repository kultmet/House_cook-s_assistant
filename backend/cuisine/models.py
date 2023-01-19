from django.db import models

class Recipe(models.Model):
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
        'User',
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    def __str__(self):
        return self.name

