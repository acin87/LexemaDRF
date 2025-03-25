from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Класс получения токенов"""

    def create(self, validated_data):
        raise NotImplementedError("Create method is not supported.")

    def update(self, instance, validated_data):
        raise NotImplementedError("Update method is not supported.")

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = self.get_user(username)

        if not user:
            raise ValidationError({"username": ["Нет такой учетной записи"]})

        if not user.check_password(password):
            raise ValidationError({"password": ["Неверный пароль"]})

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        data = super().validate(attrs)
        return data

    @staticmethod
    def get_user(username):
        """Получаем пользователя по username"""
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    class Meta:
        """Метаданные сериализатора""" ""
        model = User
        fields = ["username", "password"]


class RegisterSerializer(serializers.ModelSerializer):
    """Класс для сериализации пользователя"""

    email = serializers.EmailField(required=True)

    class Meta:
        """Метаданные сериализатора"""

        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user