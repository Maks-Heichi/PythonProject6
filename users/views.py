"""API-контроллеры для пользователей и платежей."""

from rest_framework import generics

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией."""

    serializer_class = PaymentSerializer

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


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Профиль пользователя с историей платежей."""

    queryset = User.objects.prefetch_related("payments__paid_course", "payments__paid_lesson")
    serializer_class = UserSerializer
