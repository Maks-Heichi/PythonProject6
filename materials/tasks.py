"""Celery-задачи для курсов."""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from materials.models import Course, Subscription


@shared_task
def send_course_update_email(course_id: int) -> str:
    """Отправляет письмо подписчикам об обновлении курса."""
    course = Course.objects.filter(pk=course_id).first()
    if not course:
        return "Курс не найден"

    emails = list(
        Subscription.objects.filter(course=course)
        .exclude(user__email__isnull=True)
        .exclude(user__email="")
        .values_list("user__email", flat=True)
    )
    if not emails:
        return "Нет подписчиков для уведомления"

    subject = f"Обновление курса: {course.title}"
    message = (
        f'Курс "{course.title}" был обновлён.\n'
        f"Описание: {course.description or 'без описания'}"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )
    return f"Отправлено писем: {len(emails)}"
