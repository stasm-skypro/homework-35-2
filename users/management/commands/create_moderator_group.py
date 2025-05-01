from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from materials.models import Lesson, Course


class Command(BaseCommand):
    """
    Кастомная команда. Создаёт группу 'Модераторы' и наделяёт её правами просматривать и редактировать курсы
    и уроки.
    """

    help = "Создает группу 'Модераторы' с правами на редактирование и просмотр уроков и курсов"

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Модераторы")

        # Получаем разрешения
        lesson_perms = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Lesson),
            codename__in=["change_lesson", "view_lesson"],
        )
        course_perms = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Course),
            codename__in=["change_course", "view_course"],
        )

        # Назначаем права группе
        group.permissions.set(list(lesson_perms) + list(course_perms))
        group.save()

        self.stdout.write(self.style.SUCCESS('Группа "Модераторы" создана и права назначены'))
