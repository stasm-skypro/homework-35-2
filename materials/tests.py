from rest_framework import status
from rest_framework.test import APITestCase
from materials.models import Lesson, Course
from users.models import User


# Можно импортировать пользователя из users.models или получить через
# User = get_user_model()


# -- Тестирование CRUD операций с уроками --
class LessonCreateAPIViewTestCase(APITestCase):
    """
    Тестирует CRUD операции с уроками.
    """

    def setUp(self):
        """
        Создаёт пользователей и тестовые данные.
        :return: None
        """
        User.objects.all().delete()  # Удаление всех пользователей перед тестом

        # Создаём тестового владельца
        self.owner = User.objects.create_user(username="owner", email="owner@email.com", password="password")

        # Создаём тестовый курс
        self.course = Course.objects.create(
            name="Test Course", description="Test Course Description", owner=self.owner
        )

        # Создаём тестовый урок
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="Test Description",
            course=self.course,
            owner=self.owner,
        )

        # Создаём тестовые URL-ы
        self.lessons_create_url = "/lesson/create/"
        self.lessons_list_url = "/lesson/list/"
        self.lesson_url = f"/lesson/list/{self.lesson.id}/"
        self.lesson_update_url = f"/lesson/update/{self.lesson.id}/"
        self.lesson_delete_url = f"/lesson/delete/{self.lesson.id}/"

    def test_create_lesson_owner(self):
        """
        Проверяет создание урока владельцем.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.lessons_create_url,
            {
                "name": "New Lesson",
                "description": "New Description",
                "course": self.course.id,
            },
        )

        # Проверяем, что урок создан
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_list_lessons_authenticated(self):
        """
        Проверяет, что владелец может просматривать список уроков.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson_owner(self):
        """
        Проверяет, что владелец может просматривать свой урок.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.lesson_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_owner(self):
        """
        Проверяет, что владелец может обновлять свой урок.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(
            self.lesson_update_url,
            {
                "name": "Updated Lesson",
                "description": "Updated Description",
                "course": self.course.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lesson_owner(self):
        """
        Проверяет, что Владелец может удалять свой урок.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# -- Тестирование CRUD операций с курсами --
class CourseViewSetTestCase(APITestCase):
    """
    Тестирует CRUD операции с курсами.
    """

    def setUp(self):
        """
        Создаёт пользователей и тестовые данные.
        :return: None
        """
        User.objects.all().delete()  # Удаление всех пользователей перед тестом

        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="testpass")

        self.moderator = User.objects.create_user(
            username="moderator",
            email="moderator@example.com",
            password="testpass",
            is_moderator=True,
        )

        # -- Чтобы тесты сработали тестового модератора обязательно нужно добавить в группу модераторов
        from django.contrib.auth.models import Group

        moderators_group, created = Group.objects.get_or_create(name="Модераторы")  # Получаем группу модераторов
        moderators_group.user_set.add(self.moderator)  # Добавляем модератора в группу

        self.user = User.objects.create_user(username="user", email="user@example.com", password="testpass")

        self.course = Course.objects.create(name="Test Course", description="Test Description", owner=self.owner)

        self.list_url = "/course/"
        self.course_url = f"/course/{self.course.id}/"

    def test_create_course_owner(self):
        """
        Проверяет, что владелец может создать курс.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        data = {"name": "New Course", "description": "New Description"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_course_unauthenticated(self):
        """
        Проверяет, что неавторизованный пользователь не может создать курс.
        :return: None
        """
        data = {"name": "New Course", "description": "New Description"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_courses_authenticated(self):
        """
        Проверяет, что авторизованный пользователь может получить список курсов.
        :return: None
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_courses_unauthenticated(self):
        """
        Проверяет, что неавторизованный пользователь не может получить список курсов.
        :return: None
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_course_owner(self):
        """
        Проверяет, что владелец может просматривать курс.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.course_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course_moderator(self):
        """
        Проверяет, что Модератор может просматривать курс.
        :return: None
        """
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.course_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course_other_user(self):
        """
        Проверяет, что обычный пользователь не может просматривать чужой курс.
        :return: None
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.course_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_course_owner(self):
        """
        Проверяет, что владелец может обновить курс.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        data = {"name": "Updated Course", "description": "Updated Description"}
        response = self.client.put(self.course_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_course_moderator(self):
        """
        Проверяет, что модератор может обновить курс.
        :return: None
        """
        self.client.force_authenticate(user=self.moderator)
        data = {"name": "Updated Course", "description": "Updated Description"}
        response = self.client.put(self.course_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_course_other_user(self):
        """
        Проверяет, что обычный пользователь не может обновить чужой курс.
        :return: None
        """
        self.client.force_authenticate(user=self.user)
        data = {"name": "Updated Course", "description": "Updated Description"}
        response = self.client.put(self.course_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_course_owner(self):
        """
        Проверяет, что владелец может удалить курс.
        :return: None
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.course_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_course_moderator(self):
        """
        Проверяет, что модератор не может удалить курс.
        :return: None
        """
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.course_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
