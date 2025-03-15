from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """ Класс сериализатора для модели пользователя """
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")
