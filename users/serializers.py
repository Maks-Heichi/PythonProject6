"""Сериализаторы для пользователей и платежей."""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from materials.models import Course, Lesson
from users.models import Payment, User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Сериализатор для получения JWT-токена."""

    @classmethod
    def get_token(cls, user):
        """Добавляет пользовательские поля в токен."""
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        return token


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        )

    def validate_email(self, value):
        """Проверяет, что email ещё не занят."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def create(self, validated_data):
        """Создаёт пользователя с хешированным паролем."""
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "payment_history",
        )
        read_only_fields = ("email",)

    def get_payment_history(self, obj):
        """Возвращает историю платежей пользователя."""
        return PaymentHistorySerializer(obj.payments.all(), many=True).data


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор обновления пользователя."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        )
        read_only_fields = ("email",)


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор платежа."""

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentCourseSerializer(serializers.ModelSerializer):
    """Краткий сериализатор курса в платеже."""

    class Meta:
        model = Course
        fields = ("id", "title", "description")


class PaymentLessonSerializer(serializers.ModelSerializer):
    """Краткий сериализатор урока в платеже."""

    class Meta:
        model = Lesson
        fields = ("id", "title", "description", "video_url", "course")


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Сериализатор истории платежей с вложенными данными."""

    paid_course = PaymentCourseSerializer(read_only=True)
    paid_lesson = PaymentLessonSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
