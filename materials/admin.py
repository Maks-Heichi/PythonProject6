"""Регистрация моделей в админ-панели Django."""

from django.contrib import admin

from materials.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админка курса."""

    list_display = ("id", "title")
    search_fields = ("title",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Админка урока."""

    list_display = ("id", "title", "course")
    search_fields = ("title",)
    list_filter = ("course",)
