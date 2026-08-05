"""Адреса API для пользователей и платежей."""

from django.urls import path

from users.views import (
    MyTokenObtainPairView,
    MyTokenRefreshView,
    PaymentListAPIView,
    UserCreateAPIView,
    UserDestroyAPIView,
    UserListAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
)

urlpatterns = [
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("users/register/", UserCreateAPIView.as_view(), name="user-register"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserRetrieveAPIView.as_view(), name="user-retrieve"),
    path("users/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
]
