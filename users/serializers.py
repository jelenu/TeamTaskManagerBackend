from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'password', 'email')  # Agrega cualquier otro campo que quieras
