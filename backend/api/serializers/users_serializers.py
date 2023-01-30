from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Follow
from cuisine.models import Recipe

# from api.serializers.cuisine_serializers import RecipeSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

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
    
    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('А username не может быть "me"')
        return value



    

