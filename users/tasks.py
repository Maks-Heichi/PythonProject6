"""Celery-задачи для пользователей."""

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def block_inactive_users() -> str:
    """Блокирует пользователей без входа более месяца."""
    month_ago = timezone.now() - timedelta(days=30)
    updated = User.objects.filter(
        last_login__lt=month_ago,
        is_active=True,
    ).update(is_active=False)
    return f"Заблокировано пользователей: {updated}"
