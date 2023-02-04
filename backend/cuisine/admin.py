from django import forms
from django.contrib import admin 
from django.db import models
from django.contrib.admin import widgets

from cuisine.models import Recipe, Tag, IngredientRecipe, Favorite, Order, BaseIngredientWithUnits, TagRecipe


# class TagChoiceBox(admin.)


class IngredienteInline(admin.TabularInline):
    # formfield_overrides = {models.ManyToManyField: {'widget': widgets.ForeignKeyRawIdWidget}}
    model = IngredientRecipe
    extra = 0

class TagInline(admin.StackedInline):
    model = TagRecipe
    extra = 0

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
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

    def get_author(self, request, obj):
        return request.user
    
    # def get_tags(self,obj):
    #     return [tag for tag in obj.tags.all()]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
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
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )

@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tag',
        'recipe',
    )