from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from lms.models import Course, Lesson, CourseSubscription


class LessonCRUDAndSubscriptionTests(APITestCase):
    """
    Набор тестов для проверки CRUD-операций с уроками и подписками на курсы.
    Тестируются права доступа различных типов пользователей и валидация данных.
    """

    def setUp(self):
        """
        Подготовка тестового окружения:
        - Создание тестовых пользователей (владелец, другой пользователь, модератор)
        - Настройка группы модераторов
        - Создание тестовых курсов и уроков
        """
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass1234"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@example.com", password="pass1234"
        )
        self.moderator_user = User.objects.create_user(
            username="moder", email="moder@example.com", password="pass1234"
        )

        self.mod_group, _ = Group.objects.get_or_create(name="Moderators")
        self.moderator_user.groups.add(self.mod_group)


        self.course_owner = Course.objects.create(
            name="Python 101",
            description="Base course",
            owner=self.owner,
        )
        self.course_other = Course.objects.create(
            name="Django 101",
            description="Other course",
            owner=self.other_user,
        )
        self.lesson_owner = Lesson.objects.create(
            course=self.course_owner,
            name="Intro",
            description="Lesson desc",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            owner=self.owner,
        )
        self.lesson_other = Lesson.objects.create(
            course=self.course_other,
            name="Setup",
            description="Setup desc",
            video_url="https://www.youtube.com/watch?v=oHg5SJYRHA0",
            owner=self.other_user,
        )

    def test_lesson_list_owner_sees_only_their_lessons(self):
        """
        Проверка, что владелец видит только свои уроки в списке:
        - Владелец должен видеть только созданные им уроки
        - Уроки других пользователей должны быть скрыты
        """
        self.client.force_authenticate(self.owner)
        url = reverse("lesson-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        returned_names = [item["name"] for item in resp.data["results"]]
        self.assertIn(self.lesson_owner.name, returned_names)
        self.assertNotIn(self.lesson_other.name, returned_names)

    def test_lesson_list_moderator_sees_all_lessons(self):
        """
        Проверка, что модератор видит все уроки в системе:
        - Модератор должен видеть уроки всех пользователей
        - В списке должны отображаться как собственные уроки, так и уроки других пользователей
        """
        self.client.force_authenticate(self.moderator_user)
        url = reverse("lesson-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        returned_names = [item["name"] for item in resp.data["results"]]
        self.assertIn(self.lesson_owner.name, returned_names)
        self.assertIn(self.lesson_other.name, returned_names)

    def test_lesson_retrieve_owner_allowed(self):
        """
        Проверка доступа владельца к детальной информации урока:
        - Владелец должен иметь доступ к подробной информации о своем уроке
        - Запрос должен возвращать корректные данные урока
        """
        self.client.force_authenticate(self.owner)
        url = reverse("lesson-detail", args=[self.lesson_owner.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], self.lesson_owner.id)

    def test_lesson_retrieve_moderator_allowed(self):
        """
        Проверка доступа модератора к детальной информации любого урока:
        - Модератор должен иметь доступ к информации о любом уроке
        - Запрос должен возвращать корректные данные урока
        """
        self.client.force_authenticate(self.moderator_user)
        url = reverse("lesson-detail", args=[self.lesson_other.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], self.lesson_other.id)

    def test_lesson_retrieve_forbidden_for_non_owner_non_moderator(self):
        """
        Проверка ограничения доступа к уроку для обычного пользователя:
        - Пользователь не должен иметь доступ к урокам, которые ему не принадлежат
        - Система должна возвращать ошибку 403 Forbidden
        """
        self.client.force_authenticate(self.owner)
        url = reverse("lesson-detail", args=[self.lesson_other.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_create_by_owner_allowed(self):
        """
        Проверка создания урока владельцем:
        - Владелец должен иметь возможность создать новый урок
        - Созданный урок должен быть автоматически привязан к владельцу
        - Все поля урока должны быть корректно сохранены
        """
        self.client.force_authenticate(self.owner)
        url = reverse("lesson-list")
        payload = {
            "course": self.course_owner.id,
            "name": "New lesson",
            "description": "desc",
            "video_url": "https://www.youtube.com/watch?v=video12345",
        }
        resp = self.client.post(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_lesson = Lesson.objects.get(pk=resp.data["id"])
        self.assertEqual(new_lesson.owner, self.owner)

    def test_lesson_create_by_moderator_forbidden(self):
        """
        Проверка запрета создания уроков модератором:
        - Модератор не должен иметь возможность создавать новые уроки
        - Система должна возвращать ошибку 403 Forbidden
        """
        self.client.force_authenticate(self.moderator_user)
        url = reverse("lesson-list")
        payload = {
            "course": self.course_owner.id,
            "name": "Mod lesson",
            "description": "desc",
            "video_url": "https://www.youtube.com/watch?v=video12345",
        }
        resp = self.client.post(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_create_with_invalid_video_url_fails(self):
        """
        Проверка валидации URL видео при создании урока:
        - Система должна отклонять URL, не соответствующие YouTube
        - Должна возвращаться ошибка 400 Bad Request с указанием проблемы в поле video_url
        """
        self.client.force_authenticate(self.owner)
        url = reverse("lesson-list")
        payload = {
            "course": self.course_owner.id,
            "name": "Bad URL",
            "description": "desc",
            "video_url": "https://vimeo.com/12345",
        }
        resp = self.client.post(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_url", resp.data)

    def test_lesson_update_owner_allowed(self):
        """
        Проверка обновления урока владельцем:
        - Владелец должен иметь возможность изменять свои уроки
        - Изменения должны корректно сохраняться в базе данных
        """
        self.client.force_authenticate(self.owner)
        url = reverse("lesson-detail", args=[self.lesson_owner.pk])
        payload = {"name": "Intro updated"}
        resp = self.client.patch(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.lesson_owner.refresh_from_db()
        self.assertEqual(self.lesson_owner.name, "Intro updated")

    def test_lesson_update_moderator_allowed(self):
        """
        Проверка обновления урока модератором:
        - Модератор должен иметь возможность изменять любые уроки
        - Изменения должны корректно сохраняться в базе данных
        """
        self.client.force_authenticate(self.moderator_user)
        url = reverse("lesson-detail", args=[self.lesson_other.pk])
        payload = {"name": "Setup updated"}
        resp = self.client.patch(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.lesson_other.refresh_from_db()
        self.assertEqual(self.lesson_other.name, "Setup updated")

    def test_lesson_update_forbidden_for_non_owner_non_moderator(self):
        """
        Проверка запрета обновления урока обычным пользователем:
        - Пользователь не должен иметь возможность изменять чужие уроки
        - Система должна возвращать ошибку 403 Forbidden
        """
        self.client.force_authenticate(self.owner)
        url = reverse("lesson-detail", args=[self.lesson_other.pk])
        payload = {"name": "Hack"}
        resp = self.client.patch(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_owner_allowed(self):
        """
        Проверка удаления урока владельцем:
        - Владелец должен иметь возможность удалять свои уроки
        - После удаления урок не должен присутствовать в базе данных
        """
        self.client.force_authenticate(self.owner)
        url = reverse("lesson-detail", args=[self.lesson_owner.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson_owner.pk).exists())

    def test_lesson_delete_moderator_forbidden_even_if_owner(self):
        """
        Проверка запрета удаления уроков модератором:
        - Модератор не должен иметь возможность удалять уроки, даже если является их владельцем
        - Система должна возвращать ошибку 403 Forbidden
        - Урок должен оставаться в базе данных
        """
        mod_owned_lesson = Lesson.objects.create(
            course=self.course_owner,
            name="Mod owned",
            description="",
            video_url="https://www.youtube.com/watch?v=abcd",
            owner=self.moderator_user,
        )
        self.client.force_authenticate(self.moderator_user)
        url = reverse("lesson-detail", args=[mod_owned_lesson.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(pk=mod_owned_lesson.pk).exists())

    def test_subscribe_and_unsubscribe_flow(self):
        """
        Проверка полного цикла подписки/отписки от курса
        """
        self.client.force_authenticate(self.owner)
        
        # Очищаем все подписки перед тестом
        CourseSubscription.objects.all().delete()
        
        # Проверяем, что изначально подписки нет
        self.assertFalse(
            CourseSubscription.objects.filter(
                user=self.owner, 
                course=self.course_other
            ).exists()
        )
        
        subscribe_url = reverse("course-subscribe", args=[self.course_other.id])
        unsubscribe_url = reverse("course-unsubscribe", args=[self.course_other.id])

        # Подписываемся
        resp = self.client.post(subscribe_url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CourseSubscription.objects.filter(
                user=self.owner, 
                course=self.course_other
            ).exists()
        )

        # Пробуем подписаться повторно
        resp = self.client.post(subscribe_url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", resp.data)

        # Отписываемся
        resp = self.client.delete(unsubscribe_url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            CourseSubscription.objects.filter(
                user=self.owner, 
                course=self.course_other
            ).exists()
        )

        # Пробуем отписаться повторно
        resp = self.client.delete(unsubscribe_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_requires_authentication(self):
        """
        Проверка требования аутентификации для подписки:
        - Неавторизованный пользователь не должен иметь возможность подписаться на курс
        - Система должна возвращать ошибку 401 Unauthorized
        """
        # no auth
        subscribe_url = reverse("course-subscribe", args=[self.course_other.id])
        resp = self.client.post(subscribe_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- Toggle subscription APIView ----------
    def test_toggle_subscription_and_course_serializer_flag(self):
        """
        Проверка переключения подписки и отображения статуса в сериализаторе курса:
        - Подписка должна корректно добавляться и удаляться
        - Флаг is_subscribed должен корректно отображаться в API курсов
        - Статус подписки должен обновляться в реальном времени
        """
        self.client.force_authenticate(self.owner)
        toggle_url = reverse("course-subscription")

        # Initially not subscribed
        self.assertFalse(
            CourseSubscription.objects.filter(
                user=self.owner, course=self.course_owner
            ).exists()
        )

        # Toggle add
        resp = self.client.post(toggle_url, data={"course": self.course_owner.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("message"), "Подписка добавлена")
        self.assertTrue(
            CourseSubscription.objects.filter(
                user=self.owner, course=self.course_owner
            ).exists()
        )

        # Check is_subscribed via Course serializer in list
        courses_url = reverse("course-list")
        list_resp = self.client.get(courses_url)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        # find our course in results (pagination may apply)
        found = None
        for item in list_resp.data["results"]:
            if item["name"] == self.course_owner.name:
                found = item
                break
        self.assertIsNotNone(found)
        self.assertTrue(found.get("is_subscribed"))

        # Toggle remove
        resp = self.client.post(toggle_url, data={"course": self.course_owner.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("message"), "Подписка удалена")
        self.assertFalse(
            CourseSubscription.objects.filter(
                user=self.owner, course=self.course_owner
            ).exists()
        )