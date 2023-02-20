import django_filters
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError
from cuisine.models import Recipe, Tag


class RecipeFilterSet(filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = django_filters.BooleanFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='is_in_shopping_cart_filter', distinct=True
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        )

    def tags_filter(self, queryset, name, value):
        queryset = queryset.filter(tags__slug__in=value).distinct()
        return queryset

    def binary_validator(self, name, value):
        if value < 0 or value > 1:
            raise ValidationError(
                f'Параметр "{name}" может иметь значения "0" или "1".'
            )
        return value

    def returns_orthodox_queryset(self, value, result, exclude_resilt):
        querysets = {0: exclude_resilt, 1: result}
        try:
            return querysets[value]
        except KeyError:
            raise ValidationError(f'Что-то пошло не так {KeyError}')

    def is_favorited_filter(self, queryset, name, value):
        """
        Фильтр Для поля is_favorited.
        Выводит только избранное или исключает избранное.
        """
        self.binary_validator(name=name, value=value)
        user = self.request.user
        if user.is_anonymous:
            return queryset
        favorite_recipes = queryset.filter(favorites__user=user)
        exclude_favorite_recipes = queryset.exclude(
            favorites__user=user
        )
        return self.returns_orthodox_queryset(
            value=value,
            result=favorite_recipes,
            exclude_resilt=exclude_favorite_recipes
        )

    def is_in_shopping_cart_filter(self, queryset, name, value):
        self.binary_validator(name=name, value=value)
        user = self.request.user
        if user.is_anonymous:
            return queryset
        in_order_recipes = queryset.filter(orders__user=user)
        exclude_in_order_recipes = queryset.exclude(orders__user=user)
        return self.returns_orthodox_queryset(
            value=value,
            result=in_order_recipes,
            exclude_resilt=exclude_in_order_recipes
        )
