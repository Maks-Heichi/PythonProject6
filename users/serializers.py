"""Сериализаторы для пользователей и платежей."""

from rest_framework import serializers

from materials.models import Course, Lesson
from users.models import Payment, User


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


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    payment_history = PaymentHistorySerializer(source="payments", many=True, read_only=True)

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
