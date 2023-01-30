from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action, api_view
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import Follow
from api.serializers.cuisine_serializers import FollowSerializer

User = get_user_model()

# class FollowViewSet(
#     ListModelMixin,
#     CreateModelMixin,
#     DestroyModelMixin,
#     GenericViewSet
# ):
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer
#     permission_classes = (IsAuthenticated,)
# @api_view(http_method_names=['GET',])
class FollowViewSet(GenericViewSet): # ВСЕ ПЕРЕДАЛАТЬ НА VIEW ФУНКЦИИ
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, ]
    # queryset = Follow.objects.all()
    def get_queryset(self, request):
        user = get_object_or_404(User, id=request.user.id)
        return Follow.objects.filter(user=user)
    
# @action(
#     detail=False,
#     methods=['get'],
#     permission_classes=[IsAuthenticated, ],
#     # queryset=Follow.objects.all()
# )
@api_view(http_method_names=['GET', ])
def followings(request):
    user = get_object_or_404(User, id=request.user.id)
    followings = Follow.objects.filter(user=user)
    serializer = FollowSerializer(followings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


