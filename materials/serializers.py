from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Subscription
from .models import Course, Lesson
from .validators import DescriptionValidator


class LessonSerializer(serializers.ModelSerializer):
    """
    Определяет сериализатор для модели Урок.
    """

    class Meta:
        """
        Управляет поведением сериализатора урока.
        Задаёт поля модели и класс валидатора.
        """

        model = Lesson
        fields = "__all__"
        validators = [DescriptionValidator(field="description")]


class CourseSerializer(serializers.ModelSerializer):
    """
    Определяет сериализатор для модели Курс.
    """

    lessons_count = serializers.SerializerMethodField()  # Количество уроков
    is_subscribed = serializers.SerializerMethodField()  # Подписка

    @staticmethod
    def get_lessons_count(obj):
        """
        Получает количество уроков в курсе.
        :param obj: Объект курса
        :return: Количество уроков
        """
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Определяет, подписан ли текущий пользователь на курс.
        :param obj: Объект курса
        :return: True, если пользователь подписан, иначе False
        """
        user = self.context.get("request").user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, course=obj).exists()
        return False

    class Meta:
        """
        Управляет поведением сериализатора курса.
        Задаёт поля модели и класс валидатора.
        """

        model = Course
        fields = [
            "id",
            "name",
            "description",
            "lessons_count",
            "is_subscribed",
            "updated_at",
        ]
        validators = [DescriptionValidator(field="description")]


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Определяет сериализатор для детализации модели Курс.
    """

    lessons_count = serializers.SerializerMethodField()  # Количество уроков
    lessons = LessonSerializer(many=True, read_only=True)  # Уроки
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_lessons_count(obj):
        """
        Получает количество уроков в курсе.
        :param obj: Объект курса
        :return: Количество уроков
        """
        return obj.lessons.count()

    def get(self, request, course_id):
        """
        Возвращает детализацию курса.
        :param request: Запрос
        :param course_id: ID курса
        :return: Детализацию курса
        """
        course = get_object_or_404(Course, id=course_id)
        serializer = CourseSerializer(course, context={"request": request})
        return Response(serializer.data)

    class Meta:
        """
        Определяет поведение сериализатора курса.
        Задаёт поля модели в админке.
        """

        model = Course
        fields = ["name", "description", "lessons_count", "lessons"]
