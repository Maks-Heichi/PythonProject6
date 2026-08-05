"""API-контроллеры для курсов и уроков."""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson, Subscription
from materials.paginators import MaterialsPagination
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курса через ViewSet."""

    serializer_class = CourseSerializer
    pagination_class = MaterialsPagination

    def get_queryset(self):
        """Модератор видит все курсы, остальные — только свои."""
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        """Права доступа в зависимости от action."""
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ("update", "partial_update", "retrieve"):
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, IsOwner, ~IsModer]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Привязывает курс к авторизованному пользователю."""
        serializer.save(owner=self.request.user)


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание урока."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        """Привязывает урок к авторизованному пользователю."""
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """Список уроков."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPagination

    def get_queryset(self):
        """Модератор видит все уроки, остальные — только свои."""
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение одного урока."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]

    def get_queryset(self):
        return Lesson.objects.all()


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Изменение урока."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]

    def get_queryset(self):
        return Lesson.objects.all()


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока."""

    permission_classes = [IsAuthenticated, IsOwner, ~IsModer]

    def get_queryset(self):
        return Lesson.objects.all()


class SubscriptionAPIView(APIView):
    """Установка и удаление подписки на курс."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Добавляет или удаляет подписку пользователя на курс."""
        user = request.user
        course_id = request.data.get("course_id")
        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
