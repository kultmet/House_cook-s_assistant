from django.contrib import admin

from cuisine.models import Recipe, Tag, Ingredient, Favorite, Order

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'tag',
        'ingredient',
        'coockung_time',
        'description',
        'image',
        'author',
    )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )

@admin.register(Ingredient)
class IngedientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'amount',
        'measurement_unit',
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