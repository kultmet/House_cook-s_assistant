from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404


from users.models import Follow
from cuisine.models import Recipe

# from api.serializers.cuisine_serializers import RecipeSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
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
        # print(self.context['request'].user)
        if not self.context['request'].user.is_anonymous:
            print(self.context['request'].user.is_anonymous)
            
            return Follow.objects.filter(
                user=self.context['request'].user, author=obj
            ).exists()
        else:
            print(self.context['request'].user.is_anonymous)
            return False
        # if Follow.objects.filter(
        #     user=self.context['request'].user, author=obj
        # ).exists():
        #     return True
        # else:
        #     return False
        # print(self.context['request'].user)
        # return 'fuck'
    
    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('А username не может быть "me"')
        return value



    

