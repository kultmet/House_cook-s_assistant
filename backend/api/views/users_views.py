from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import GenericViewSet

from djoser.conf import settings
from djoser.compat import get_user_email
from djoser import utils

from api.paginators import CustomPaginator
from api.serializers.users_serializers import (
    UserSerializer, FollowSerializer, CreateFollowSerializer
)
from users.models import Follow


User = get_user_model()


class CustomUserViewSet(
    ListModelMixin, CreateModelMixin, RetrieveModelMixin, GenericViewSet
):
    """
    ViewSet для создания, просмотра пользователей;
    создарие, удаление и просмотра подписок; смены пароля.
    """
    queryset = User.objects.all()
    pagination_class = CustomPaginator
    token_generator = default_token_generator
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]

    def get_serializer_class(self):
        """
        Указываем сериализаторы для создания Подписки,
        для создания Пользователя и смены пароля.
        """
        if self.action == 'follow' and self.request.method == 'POST':
            return CreateFollowSerializer
        if self.action == 'create':
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_password_retype
            return settings.SERIALIZERS.user_create
        if self.action == 'set_password':
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        return super().get_serializer_class()

    @action(['post'], detail=False, permission_classes=IsAuthenticated)
    def set_password(self, request, *args, **kwargs):
        """Обрабатывает смену пароля."""
        request.data['email'] = request.user.email
        request.data['username'] = request.user.username
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request, context
            ).send(to)
        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(
            data='Пароль успешно изменен', status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        url_path='me',
        methods=['get',],
        permission_classes=[IsAuthenticated, ],
        queryset=User.objects.all()
    )
    def me(self, request):
        """
        Профиль текущего пользователя.
        """
        user = get_object_or_404(User, id=request.user.id)
        serializer = self.get_serializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
