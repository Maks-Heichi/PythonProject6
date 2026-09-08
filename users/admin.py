"""Регистрация моделей пользователя в админ-панели Django."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Payment, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка пользователя с входом по email."""

    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "phone", "city", "is_staff")
    search_fields = ("email", "first_name", "last_name", "phone", "city")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональные данные", {"fields": ("first_name", "last_name", "phone", "city", "avatar")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админка платежей."""

    list_display = (
        "id",
        "user",
        "payment_date",
        "payment_amount",
        "payment_method",
        "status",
        "payment_status",
        "session_id",
    )
    list_filter = ("payment_method", "payment_date", "status", "payment_status")
    search_fields = ("user__email", "session_id")
    readonly_fields = (
        "stripe_product_id",
        "stripe_price_id",
        "session_id",
        "payment_link",
        "status",
        "payment_status",
    )
