from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from cuisine.models import (
    Recipe,
    Tag,
    IngredientRecipe,
    Favorite,
    Order,
    BaseIngredientWithUnits,
    TagRecipe
)


class ForModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


class IngredienteInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 0


class TagInline(admin.StackedInline):
    model = TagRecipe
    extra = 0
    max_num = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    inlines = [IngredienteInline, TagInline]
    list_display = (
        'id',
        'name',
        'get_tag',
        'get_ingeredient',
        'cooking_time',
        'description',
        'image',
        'author',
    )
    fields = (
        'name',
        ('image', 'author',),
        'description',
        'cooking_time',
    )

    def get_author(self, request, obj):
        return request.user


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    list_display = (
        'name',
        'color',
        'slug',
    )


@admin.register(BaseIngredientWithUnits)
class BaseIngredient(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    fields = (
        'name',
        'measurement_unit',
    )


@admin.register(IngredientRecipe)
class IngedientAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'get_base_ingredient',
        'amount',
        'get_measurement_unit',
        'recipe',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
        'get_recipe_id',
    )

    def get_recipe_id(self, obj):
        return obj.recipe.id


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
        'recipe_id'
    )


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'tag',
        'recipe',
    )
