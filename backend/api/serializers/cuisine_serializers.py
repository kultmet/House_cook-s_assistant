import uuid
import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError
from cuisine.models import Recipe, Tag, IngredientRecipe, BaseIngredientWithUnits, Favorite, Order, TagRecipe
from users.models import Follow
from api.serializers.users_serializers import UserSerializer

# Coral	#FF7F50 завтрак
# MediumSeaGreen	#3CB371 обед
# BlueViolet	#8A2BE2  ужин
class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тэгов."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class TagRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для привязки Тэга к Рецепту."""
    id = serializers.PrimaryKeyRelatedField(read_only=True, source='tag.id')
    name = serializers.StringRelatedField(read_only=True, source='tag.name')
    color = serializers.StringRelatedField(read_only=True, source='tag.color')
    slug = serializers.StringRelatedField(read_only=True, source='tag.slug')
    class Meta:
        model = TagRecipe
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода Ингредиента к Рецепту. Только чтение."""
    name = serializers.StringRelatedField(
        read_only=True, source='base_ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        read_only=True, source='base_ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='base_ingredient.id'
    )
    
    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )


class BaseIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для привязки Ингредиента к Рецепту."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)
    class Meta:
        model = BaseIngredientWithUnits
        fields = (
            'id',
            'amount',
            'name',
            'measurement_unit',
        )
        read_only_fields = (
            'name',
            'measurement_unit',
        )


class Base64ToImageField(serializers.ImageField):
    """Поле картинки."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}'
            )
        return super().to_internal_value(data)


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания Рецепта."""
    ingredients = BaseIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())#
    image = Base64ToImageField()
    text = serializers.CharField(source='description')
    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
    
    def to_representation(self, instance):
        """После создания рецепта, перенаправляет на Сериализатор Рецепта(чтение)."""
        return RecipeSerializer(instance=instance, context=self.context).data
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            base_ingredient = get_object_or_404(
                BaseIngredientWithUnits,
                id=ingredient['id']
            )
            IngredientRecipe.objects.create(
                base_ingredient=base_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = instance
        for tag in tags:
            TagRecipe.objects.get_or_create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            base_ingredient = get_object_or_404(
                BaseIngredientWithUnits,
                id=ingredient['id']
            )
            IngredientRecipe.objects.get_or_create(
                base_ingredient=base_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        return super().update(instance, validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов. Только чтоение."""
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, source='ingredientrecipe')
    tags = TagRecipeSerializer(many=True, source='tagrecipe', read_only=True)
    text = serializers.CharField(source='description')
    image = Base64ToImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def boolean_harvester(self, sample, obj):
        """
        Проверяет, что запрос не анонимный.
        Возвращает наличие обьектов Favorite и Order.
        """
        if not self.context['request'].user.is_anonymous:
            return sample.objects.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        else:
            return False

    def get_is_favorited(self, obj):
        return self.boolean_harvester(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.boolean_harvester(Order, obj)




class FavoriteSerializer(serializers.ModelSerializer):
    """Сериолизатор для Избранного Рецепта."""
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.StringRelatedField(source='recipe.name', read_only=True)
    image = serializers.StringRelatedField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )
    class Meta:
        model = Favorite
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def validate_empty_values(self, data):
        """Формируем словарь context и проверяем ключи."""
        try:
            self.context['request'] = data['request']
            self.context['recipe_id'] = data['recipe_id']
        except KeyError:
            raise ValidationError('KeyError')
        return super().validate_empty_values(data)
    
    def validate(self, data):
        if self.context['request'].user.is_anonymous:
            raise ValidationError(
                'Данные пользователя не были предоставлены.'
            )
        try:
            request = self.context['request']
            user = request.user
            recipe_id = self.context['recipe_id']
        except KeyError:
            raise ValidationError('KeyError')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        data['recipe'] =  recipe
        data['user'] = user
        if request.method == 'POST':
            if recipe.favorites.select_related('recipe').filter(user=user):
                raise ValidationError(
                    'Рецепт уже в избранном'
                )
        if request.method == 'DELETE':
            print('request.method == DELETE')
            if not recipe.favorites.select_related('recipe').filter(user=user).exists():
                raise ValidationError(
                    'Рецепта еще нет в избранном'
                )
        return data


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для Корзины Покупок."""
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.StringRelatedField(source='recipe.name', read_only=True)
    image = serializers.StringRelatedField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time', read_only=True)
    class Meta:
        model = Order
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
    
    def validate_empty_values(self, data):
        """Формируем словарь context и проверяем ключи."""
        try:
            self.context['request'] = data['request']
            self.context['recipe_id'] = data['recipe_id']
        except KeyError:
            raise ValidationError('KeyError')
        return super().validate_empty_values(data)
    
    def validate(self, data):
        if self.context['request'].user.is_anonymous:
            raise ValidationError(
                'Данные пользователя не были предоставлены.'
            )
        try:
            request = self.context['request']
            user = request.user
            recipe_id = self.context['recipe_id']
        except KeyError:
            raise ValidationError('KeyError')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        data['recipe'] =  recipe
        data['user'] = user
        if request.method == 'POST':
            if recipe.orders.select_related('recipe').filter(user=user):
                raise ValidationError(
                    'Рецепт уже в списке покупок'
                )
        if request.method == 'DELETE':
            if not recipe.orders.select_related('recipe').filter(user=user).exists():
                raise ValidationError(
                    'Рецепта еще нет в списке покупок'
                )
        return data
