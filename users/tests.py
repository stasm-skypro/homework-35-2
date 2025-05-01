from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from materials.models import Course
from users.models import Subscription

User = get_user_model()


class SubscriptionAPIViewTestCase(APITestCase):
    """
    Определяет тесты для подписки на курс.
    """

    def setUp(self):
        """
        Создаёт тестовые данные.
        :param self: Объект класса
        """

        # Создаём пользователей
        self.user = User.objects.create_user(username="user1", email="user1@email", password="password123")
        self.other_user = User.objects.create_user(username="user2", email="user2@email", password="password123")

        # Создаём тестовый курс
        self.course = Course.objects.create(name="Test Course", description="Test Description", owner=self.user)

        # URL для подписки
        self.subscription_url = "/users/subscription/"

        # Данные для подписки
        self.data = {"course_id": self.course.id}

    def test_subscribe_to_course(self):
        """
        Тест подписки пользователя на курс.
        :param self: Объект класса
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscription_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """
        Тест отписки пользователя от курса.
        :param self: Объект класса
        """
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscription_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_unauthenticated(self):
        """
        Проверяет, что неавторизованный пользователь не может подписаться.
        :param self: Объект класса
        """
        response = self.client.post(self.subscription_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_to_own_course(self):
        """
        Тест подписки на собственный курс (допустимо или нет).
        :param self: Объект класса
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscription_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscribe_already_subscribed(self):
        """
        Проверяет повторную подписку (должно быть обработано корректно).
        :param self: Объект класса
        """
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscription_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  # Отписка, если подписан

    def test_subscribe_other_user(self):
        """
        Тест подписки другого пользователя.
        :param self: Объект класса
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.subscription_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.other_user, course=self.course).exists())


class UserViewSetTestCase(APITestCase):
    """
    Определяет тесты для UserViewSet.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            first_name="Donald",
            last_name="Trump",
            password="adminpass",
        )

        self.client.force_authenticate(user=self.user)
        self.user_url = f"/users/user/{self.user.id}/"
        self.list_url = "/users/user/"

    def get_token(self, user):
        """
        Получяет JWT токена для пользователя.
        :param user: Объект пользователя
        :return: JWT токен
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_list_users(self):
        """
        Проверяет получение списка пользователей (только для авторизованных).
        :param self: Объект класса
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user(self):
        """
        Проверяет получение информации о пользователе.
        :param self: Объект класса
        """
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_create_user(self):
        """
        Проверяет регистрацию нового пользователя.
        :param self: Объект класса
        """
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_update_user(self):
        """
        Проверяет обновление информации о пользователе (только для владельца).
        :param self: Объект класса
        """
        data = {"username": "updateduser"}
        response = self.client.patch(self.user_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_delete_user(self):
        """
        Проверяет удаление пользователя (только для владельца).
        :param self: Объект класса
        """
        response = self.client.delete(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_permissions_update_other_user(self):
        """
        Проверяет запрет редактирования чужого профиля.
        :param self: Объект класса
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {"username": "hacked"}
        response = self.client.patch(self.user_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_delete_other_user(self):
        """
        Проверяет запрет удаления чужого профиля.
        :param self: Объект класса
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
