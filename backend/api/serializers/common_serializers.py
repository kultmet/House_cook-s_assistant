from rest_framework import serializers
from cuisine.models import Recipe


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для короткого отображеня Рецепта. Только чтение."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
