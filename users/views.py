"""API-контроллеры для пользователей и платежей."""

from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import Payment, User
from users.serializers import (
    MyTokenObtainPairSerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from users.services import StripeServiceError, retrieve_stripe_session


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
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией."""

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "course",
                openapi.IN_QUERY,
                description="ID оплаченного курса",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "lesson",
                openapi.IN_QUERY,
                description="ID оплаченного урока",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "payment_method",
                openapi.IN_QUERY,
                description="Способ оплаты: cash или transfer",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Сортировка: payment_date или -payment_date",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: PaymentSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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


class PaymentCreateAPIView(generics.CreateAPIView):
    """Создание платежа за курс через Stripe."""

    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PaymentCreateSerializer,
        responses={
            201: PaymentSerializer,
            400: openapi.Response(description="Ошибка валидации или Stripe"),
        },
        operation_description=(
            "Создаёт продукт, цену и Checkout Session в Stripe, "
            "сохраняет платёж и возвращает ссылку на оплату."
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Возвращает данные созданного платежа со ссылкой на оплату."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentStatusAPIView(APIView):
    """Проверка статуса платежа в Stripe."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получает статус Checkout Session по ID платежа в системе.",
        responses={
            200: openapi.Response(
                description="Статус платежа",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "session_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                        "payment_link": openapi.Schema(type=openapi.TYPE_STRING),
                        "payment_status": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Статус оплаты из Stripe (paid/unpaid)",
                        ),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка Stripe или нет session_id"),
            404: openapi.Response(description="Платёж не найден"),
        },
    )
    def get(self, request, pk, *args, **kwargs):
        """Синхронизирует статус платежа с Stripe Session Retrieve."""
        payment = get_object_or_404(Payment, pk=pk, user=request.user)

        if not payment.session_id:
            return Response(
                {"error": "У платежа нет session_id Stripe."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = retrieve_stripe_session(payment.session_id)
        except StripeServiceError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = session.get("status", payment.status)
        payment.save(update_fields=["status"])

        return Response(
            {
                "id": payment.id,
                "session_id": payment.session_id,
                "status": payment.status,
                "payment_link": payment.payment_link,
                "payment_status": session.get("payment_status"),
            }
        )
