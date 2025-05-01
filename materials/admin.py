from django.contrib import admin

from materials.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Отображает поля модели Курсы в админке.
    """

    list_display = (
        "name",
        "description",
    )
    list_filter = ("name",)
    ordering = ("name",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Отображает поля модели Уроки в админке.
    """

    list_display = (
        "name",
        "description",
        "course",
    )
    list_filter = ("name", "course")
    ordering = ("name",)
