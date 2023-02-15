from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from users.models import Follow
from api.serializers.users_serializers import (
    UserSerializer, FollowSerializer, CreateFollowSerializer
)
from djoser.views import UserViewSet
from api.paginators import CustomPaginator

User = get_user_model()


class MyUserViewSet(UserViewSet):
    """
    ViewSet для Пользователя и для Подписок.
    """
    queryset = User.objects.all()
    pagination_class = CustomPaginator
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,]

    def activation(self, request,args, kwargs):
        """Удаление эндпоинта."""
        return Response(status=status.HTTP_404_NOT_FOUND)

    def resend_activation(self, request, *args, kwargs):
        """Удаление эндпоинта."""
        return Response(status=status.HTTP_404_NOT_FOUND)

    def set_username(self, request,args, kwargs):
        """Удаление эндпоинта."""
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_password(self, request, args, **kwargs):
        """Удаление эндпоинта."""
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_password_confirm(self, request, *args, kwargs):
        """Удаление эндпоинта."""
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_username_confirm(self, request, *args, **kwargs):
        """Удаление эндпоинта."""
        return Response(status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        """Указываем сериализатор для создания Подписки."""
        if self.action == 'follow' and self.request.method == 'POST':
            return CreateFollowSerializer
        return super().get_serializer_class()

    @action(
        methods=['get',],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        serializer_class=FollowSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def followings(self, request):
        """Список Подписок."""
        user = get_object_or_404(User, id=request.user.id)
        queryset = self.filter_queryset(
            User.objects.filter(following__user=user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        serializer_class=CreateFollowSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def follow(self, request, id):
        """Подписаться на автора, Отписаться от автора."""
        data = {}
        data['request'] = request
        data['view'] = self
        if request.method == 'POST':
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(
                user=serializer.validated_data['user'],
                author=serializer.validated_data['author']
            )
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        author = serializer.validated_data['author']
        instance = get_object_or_404(Follow, user=user, author=author)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
