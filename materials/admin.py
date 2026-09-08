"""Регистрация моделей в админ-панели Django."""

from django.contrib import admin

from materials.models import Course, Lesson, Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админка курса."""

    list_display = ("id", "title", "owner")
    search_fields = ("title",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Админка урока."""

    list_display = ("id", "title", "course", "owner")
    search_fields = ("title",)
    list_filter = ("course",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = ("id", "user", "course")
    list_filter = ("course",)
    search_fields = ("user__email", "course__title")
