from rest_framework import serializers
from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Определяет сериализатор для списка платежей.
    """

    class Meta:
        """
        Определяет поля модели в админке.
        """

        model = Payment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """
    Определяет сериализатор для списка пользователей.
    """

    payments = PaymentSerializer(many=True, read_only=True).data

    class Meta:
        """
        Определяет поля модели в админке.
        """

        model = User
        fields = ["id", "username", "email"]


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Определяет сериализатор для детальной информации о пользователе.
    """

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        """
        Определяет поля модели в админке.
        """

        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "is_staff",
            "is_active",
            "date_joined",
            "payments",
        ]
        extra_kwargs = {"password": {"write_only": True}}


class RegisterSerializer(serializers.ModelSerializer):
    """
    Определяет сериализатор для регистрации пользователя.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        """
        Определяет поля модели в админке.
        """

        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        """
        Создаёт нового пользователя.
        :param validated_data: Данные для создания пользователя.
        :return: Объект пользователя.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
