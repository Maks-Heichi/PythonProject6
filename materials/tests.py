"""Тесты CRUD уроков и подписок на курс."""

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonCRUDTestCase(APITestCase):
    """Тесты CRUD для уроков."""

    def setUp(self):
        """Создаёт пользователей, курс и урок для тестов."""
        self.owner = User.objects.create_user(email="owner@test.com", password="12345678")
        self.other = User.objects.create_user(email="other@test.com", password="12345678")
        self.moder = User.objects.create_user(email="moder@test.com", password="12345678")

        group, _ = Group.objects.get_or_create(name="moderators")
        self.moder.groups.add(group)

        self.course = Course.objects.create(title="Python", description="Курс", owner=self.owner)
        self.lesson = Lesson.objects.create(
            title="Intro",
            description="Первый урок",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            course=self.course,
            owner=self.owner,
        )

    def test_create_lesson_owner(self):
        """Владелец может создать урок."""
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Lesson 2",
            "description": "Второй урок",
            "video_url": "https://youtube.com/watch?v=abc123",
            "course": self.course.id,
        }
        response = self.client.post("/lessons/create/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], self.owner.id)

    def test_create_lesson_forbidden_url(self):
        """Нельзя создать урок со сторонней ссылкой."""
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Bad lesson",
            "video_url": "https://example.com/video",
            "course": self.course.id,
        }
        response = self.client.post("/lessons/create/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_lesson_moder_forbidden(self):
        """Модератор не может создать урок."""
        self.client.force_authenticate(user=self.moder)
        data = {
            "title": "Moder lesson",
            "course": self.course.id,
            "video_url": "https://youtube.com/watch?v=abc123",
        }
        response = self.client.post("/lessons/create/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_lessons_owner(self):
        """Владелец видит свои уроки."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_lesson_owner(self):
        """Владелец может получить свой урок."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f"/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Intro")

    def test_retrieve_lesson_other_forbidden(self):
        """Чужой пользователь не может получить урок."""
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f"/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_owner(self):
        """Владелец может обновить урок."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f"/lessons/{self.lesson.id}/update/",
            {"title": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated")

    def test_update_lesson_moder(self):
        """Модератор может обновить чужой урок."""
        self.client.force_authenticate(user=self.moder)
        response = self.client.patch(
            f"/lessons/{self.lesson.id}/update/",
            {"title": "Moder update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lesson_owner(self):
        """Владелец может удалить урок."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f"/lessons/{self.lesson.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_delete_lesson_moder_forbidden(self):
        """Модератор не может удалить урок."""
        self.client.force_authenticate(user=self.moder)
        response = self.client.delete(f"/lessons/{self.lesson.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    """Тесты подписки на курс."""

    def setUp(self):
        """Создаёт пользователя и курс для тестов подписки."""
        self.user = User.objects.create_user(email="sub@test.com", password="12345678")
        self.owner = User.objects.create_user(email="courseowner@test.com", password="12345678")
        self.course = Course.objects.create(title="Django", description="Курс", owner=self.owner)

    def test_subscribe(self):
        """Пользователь может подписаться на курс."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/course/subscribe/", {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe(self):
        """Повторный запрос удаляет подписку."""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/course/subscribe/", {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_unauthenticated(self):
        """Без авторизации подписка недоступна."""
        response = self.client.post("/course/subscribe/", {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_is_subscribed_flag(self):
        """В ответе курса есть признак подписки."""
        Subscription.objects.create(user=self.owner, course=self.course)
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f"/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])
