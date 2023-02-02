# from io import BytesIO, StringIO
import uuid
import base64
from PIL import Image

import webcolors
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.core.files.base import ContentFile
from cuisine.models import Recipe, Tag, IngredientRecipe, BaseIngredientWithUnits
from users.models import Follow
from api.serializers.users_serializers import UserSerializer

# Coral	#FF7F50 завтрак
# MediumSeaGreen	#3CB371 обед
# BlueViolet	#8A2BE2  ужин

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )

# class AmountIngredient(serializers.ModelSerializer):
#     class Meta:
#         model = IngredientRecipe
#         fields = (
#             'amount'
#         )


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(read_only=True)
    measurement_unit = serializers.StringRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        queryset=BaseIngredientWithUnits.objects.all(),
    )
    amount = serializers.SerializerMethodField()
    # amount = 
    
    class Meta:
        model = IngredientRecipe
        # model = BaseIngredientWithUnits
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )
    
    def get_amount(self, obj):
        print(obj)
        ingredient_recipe = get_object_or_404(IngredientRecipe, base_ingredient=obj)
        return ingredient_recipe.amount


class Base64ToImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
        return super().to_internal_value(data)

class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    # tags = TagSerializer(many=True, read_only=True, source='tag')
    # tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    ingredients = IngredientSerializer(many=True)
    text = serializers.CharField(source='description')
    image = Base64ToImageField()
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            # 'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'coockung_time',   
        )
    def to_representation(self, instance):
        print('instance---',instance)
        return super().to_representation(instance)

    def to_internal_value(self, data):
        print('data----',data)
        
        return super().to_internal_value(data)
    
    def validated_data(self):
        return super().validated_data

    def validate(self, attrs):
        # if not attrs['tags']:
        #     raise serializers.ValidationError(
        #         'Теги обязательны'
        #     )
        print('attrs----', attrs)
        return super().validate(attrs)
    
    # def create(self, validated_data):
    #     print(validated_data)
    #     # tags = 
    #     validated_data['author'] = self.context['request'].user
    #     recipe = Recipe.objects.create(**validated_data)
    #     return recipe


class FollowSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        fields = ('author', 'recipes',)
        model = Follow
    
    def validated_data(self):
        return super().validated_data
    
    
    
    
    
    # def get_recipes_count(self, obj):
    #     return len(self.recipes)