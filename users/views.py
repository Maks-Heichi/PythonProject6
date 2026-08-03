"""API-контроллеры для пользователей и платежей."""

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import Payment, User
from users.serializers import (
    MyTokenObtainPairSerializer,
    PaymentSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class MyTokenObtainPairView(TokenObtainPairView):
    """Получение JWT access и refresh токенов."""

    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]


class MyTokenRefreshView(TokenRefreshView):
    """Обновление JWT access токена."""

    permission_classes = [AllowAny]


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация пользователя."""

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserListAPIView(generics.ListAPIView):
    """Список пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Профиль пользователя с историей платежей."""

    queryset = User.objects.prefetch_related("payments__paid_course", "payments__paid_lesson")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserUpdateAPIView(generics.UpdateAPIView):
    """Обновление пользователя."""

    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]


class UserDestroyAPIView(generics.DestroyAPIView):
    """Удаление пользователя."""

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией."""

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Фильтрует и сортирует платежи по query params."""
        queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson").all()

        course_id = self.request.query_params.get("course")
        lesson_id = self.request.query_params.get("lesson")
        payment_method = self.request.query_params.get("payment_method")
        ordering = self.request.query_params.get("ordering")

        if course_id:
            queryset = queryset.filter(paid_course_id=course_id)
        if lesson_id:
            queryset = queryset.filter(paid_lesson_id=lesson_id)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        if ordering in ("payment_date", "-payment_date"):
            queryset = queryset.order_by(ordering)

        return queryset
