"""Сериализаторы для курса и урока."""

from rest_framework import serializers

from materials.models import Course, Lesson, Subscription
from materials.validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока."""

    video_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[validate_youtube_url],
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[validate_youtube_url],
    )

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("owner",)


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса."""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[validate_youtube_url],
    )

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе."""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя на курс."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=obj).exists()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "preview",
            "description",
            "owner",
            "lessons_count",
            "lessons",
            "is_subscribed",
        )
        read_only_fields = ("owner",)
