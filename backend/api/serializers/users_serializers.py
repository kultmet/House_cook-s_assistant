from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import ValidationError

from api.serializers.common_serializers import ShortRecipeSerializer
from users.models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для Пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_anonymous:
            return Follow.objects.filter(
                user=self.context['request'].user, author=obj
            ).exists()
        else:
            return False

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('А username не может быть "me"')
        return value


class FollowSerializer(UserSerializer):
    """Сериализатор Подписки на автора. Только чтение."""
    id = serializers.IntegerField(read_only=True)
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        author = obj
        if not self.context['request'].user.is_anonymous:
            return Follow.objects.filter(
                user=self.context['request'].user, author=author
            ).exists()
        else:
            return False

    def get_recipes_count(self, obj):
        author = obj
        recipes_count = author.recipes.select_related(
            'author'
        ).aggregate(recipes_count=Count('id'))
        return recipes_count['recipes_count']


class CreateFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для Создания экземпляра подписки."""
    class Meta:
        model = Follow
        fields = ()

    def validate_empty_values(self, data):
        print(data, 'valida empty')
        try:
            self.context['request'] = data['request']
            self.context['view'] = data['view']
        except KeyError:
            raise ValidationError('KeyError')
        return super().validate_empty_values(data)

    def validate(self, data):
        try:
            request = self.context['request']
            user = request.user
            author_id = self.context['view'].kwargs.get('id')
        except KeyError:
            raise ValidationError('KeyError')
        author = get_object_or_404(User, id=author_id)
        data['author'] = author
        data['user'] = user
        if request.method == 'POST':
            if Follow.objects.filter(user=user, author=author).exists():
                raise ValidationError(
                    f'Вы уже подписаны на пользователя {author.username}'
                )
        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                raise ValidationError(
                    'Рецепта еще нет в избранном'
                )
        return data

    def to_representation(self, instance):
        """Перенаправляет на сериализатор Подписки(только чтение)"""
        instance = instance['author']
        return FollowSerializer(instance=instance, context=self.context).data
