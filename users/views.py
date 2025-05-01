import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

from materials.models import Course
from .models import User, Payment, Subscription
from .permissions import IsProfileOwner
from .serializers import (
    UserSerializer,
    PaymentSerializer,
    UserDetailSerializer,
    RegisterSerializer,
)

import logging

from .services import convert_rub_to_usd, create_price, create_checkout_session

logger = logging.getLogger(__name__)


# -- User ViewSet --
class UserViewSet(viewsets.ModelViewSet):
    """
    Определяет CRUD для пользователей (только авторизованные).
    Attributes:
        queryset (QuerySet): Список пользователей.
        serializer_class (Serializer): Сериализатор пользователей.
        authentication_classes (list): Список классов аутентификации.
        permission_classes (list): Список классов разрешений.
    """

    queryset = User.objects.all().order_by("id")

    # Аутентификация и разрешения
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        """
        Переопределяет сериализатор в зависимости от действия.
        :return: Сериализатор
        """
        if self.action in ["retrieve", "update", "partial_update"]:
            if self.request.user == self.get_object():
                return UserDetailSerializer  # Полный доступ для владельца
        elif self.action == "create":
            return RegisterSerializer
        return UserSerializer  # Ограниченный доступ для чужого профиля и списка профилей

    def get_permissions(self):
        """
        Ограничивает редактирование только владельцам.
        :return: Список разрешений
        """
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsProfileOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        Переопределяет создание пользователя.
        :param serializer:
        :return: None
        """
        serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Переопределяет создание пользователя для логгирования.
        :param request: Запрос
        :param args: Список позиционных документов
        :param kwargs: Список именованных аргументов
        :return: Ответ
        """
        self.permission_classes = [AllowAny]
        response = super().create(request, *args, **kwargs)
        logger.info(
            "Пользователь с именем %s и email %s успешно создан." % (request.data["username"], request.data["email"])
        )
        return response

    def list(self, request, *args, **kwargs):
        """
        Переопределяет получение списка пользователей для логгирования.
        :param request: Запрос
        :param args: Список позиционных документов
        :param kwargs: Список именованных аргументов
        :return: Ответ
        """
        self.permission_classes = [IsAuthenticated]
        response = super().list(request, *args, **kwargs)
        logger.info("Список пользователей успешно получен.")
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Переопределяет получение информации о пользователе для логгирования.
        :param request: Запрос
        :param args: Список позиционных документов
        :param kwargs: Список именованных аргументов
        :return: Ответ
        """
        self.permission_classes = [IsAuthenticated]
        response = super().retrieve(request, *args, **kwargs)
        logger.info("Информация о пользователе с id %s успешно получена." % kwargs["pk"])
        return response

    def update(self, request, *args, **kwargs):
        """
        Переопределяет обновление информации о пользователе для логгирования.
        :param request: Запрос
        :param args: Список позиционных документов
        :param kwargs: Список именованных аргументов
        :return: Ответ
        """
        self.permission_classes = [IsAuthenticated]
        response = super().update(request, *args, **kwargs)
        logger.info("Информация о пользователе с id %s успешно обновлена." % kwargs["pk"])
        return response

    def destroy(self, request, *args, **kwargs):
        """
        Переопределяет удаление пользователя для логгирования.
        :param request: Запрос
        :param args: Список позиционных документов
        :param kwargs: Список именованных аргументов
        :return: Ответ
        """
        self.permission_classes = [IsAuthenticated]
        response = super().destroy(request, *args, **kwargs)
        logger.info("Пользователь с id %s успешно удален." % kwargs["pk"])
        return response


# -- Payment ViewSet --
class PaymentViewSet(viewsets.ModelViewSet):
    """
    Определяет API endpoint для управления оплатами.
    Attributes:
        queryset (QuerySet): Список оплат.
        serializer_class (Serializer): Сериализатор оплаты.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Фильтрация, поиск и сортировка
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Фильтрация по конкретным полям
    filterset_fields = ["user", "course", "lesson", "payment_method"]

    # Поля, по которым можно выполнять поиск (по частичному совпадению)
    search_fields = ["user__email", "course__name", "lesson__name"]

    # Поля, по которым можно сортировать (`ordering=-date` для сортировки по убыванию)
    ordering_fields = ["date", "amount"]

    # Создание оплаты
    def perform_create(self, serializer):
        """
        Переопределяет создание оплаты.
        :param serializer: Сериализатор
        :return: None
        """
        payment = serializer.save(user=self.request.user)  # Сохраняем объект Payment
        amount_usd = convert_rub_to_usd(payment.amount)  # Доступ к полю amount
        price = create_price(amount_usd)
        session_id, session_url = create_checkout_session(price.id)

        # Обновляем созданный объект Payment
        payment.session_id = session_id
        payment.link = session_url
        payment.save()

    # Проверка статуса оплаты
    @action(detail=True, methods=["get"])
    def check_status(self, request, pk=None, drf_status=None):
        """
        Проверяет статус оплаты.
        :param request: Запрос
        :param pk: id оплаты
        :param drf_status: Статус
        :return: Ответ
        """
        payment = self.get_object()

        if not payment.session_id:
            return Response(
                {"error": "Нет session_id для проверки оплаты."},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://api.stripe.com/v1/checkout/sessions/{payment.session_id}"
        headers = {"Authorization": f"Bearer {settings.STRIPE_SECRET_KEY}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Ошибка запроса к Stripe."}, status=response.status_code)

        session_data = response.json()
        stripe_status = session_data.get("payment_status")

        # Обновляем статус в модели Payment
        if stripe_status == "paid":
            payment.status = Payment.StatusChoices.PAID  # Например, "paid"
        elif stripe_status == "unpaid":
            payment.status = Payment.StatusChoices.UNPAID  # Например, "unpaid"
        else:
            payment.status = Payment.StatusChoices.PENDING  # Например, "pending"

        payment.save()

        return Response({"payment_status": stripe_status})


# -- Subscription ViewSet --
class SubscriptionAPIView(APIView):
    """
    Определяет API для управления подписками пользователей на курсы.
    Attributes:
        permission_classes (list): Список классов разрешений
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Переопределяет создание/удаление подписки и добавляет логгирование.
        :param request: Запрос
        :param args: Список позиционных документов
        :param kwargs: Список именованных аргументов
        :return: Ответ
        """
        user = request.user
        course_id = request.data.get("course_id")

        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
            logger.info("Подписка на курс %s удалена пользователем %s", course_item, user)
            answer = status.HTTP_204_NO_CONTENT
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"
            logger.info("Подписка на курс %s добавлена пользователем %s", course_item, user)
            answer = status.HTTP_201_CREATED

        return Response({"message": message}, status=answer)
