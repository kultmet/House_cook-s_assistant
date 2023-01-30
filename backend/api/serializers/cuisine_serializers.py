from rest_framework import serializers

from cuisine.models import Recipe, Tag, Ingredient, BaseIngredientWithUnits
from users.models import Follow
from api.serializers.users_serializers import UserSerializer

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseIngredientWithUnits
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingeredients',
            'is_favorited',
            'is_in_shopping_cart'
            'name',
            'image',
            'text',
            'coockung_time',   
        )


class FollowSerializer(serializers.ModelSerializer):
    # recipes = serializers.SerializerMethodField()
    # recipes = RecipeSerializer(many=True)
    # recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('author',)
        model = Follow
    
    def validated_data(self):
        return super().validated_data
    
    
    
    
    
    # def get_recipes_count(self, obj):
    #     return len(self.recipes)