from django.db import models


class Course(models.Model):
    """
    Определяет модель курса.
    Attributes:
        name (str): Название курса,
        description (str): Описание курса,
        image (ImageField): Превью курса,
        owner (User): Владелец курса.
    """

    name = models.CharField(max_length=255, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание курса")
    image = models.ImageField(upload_to="courses/", blank=True, null=True, verbose_name="Превью курса")
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец курса",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        """
        Определяет отображение объекта курса в админке.
        :return: Название курса
        """
        return self.name

    class Meta:
        """Определяет отображение имени модели в админке."""

        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    """
    Определяет модель урока.
    Attributes:
        name (str): Название урока,
        description (str): Описание урока,
        course (Course): Курс,
        image (ImageField): Превью урока,
        video (FileField): Видео урока,
        owner (User): Владелец урока
    """

    name = models.CharField(max_length=255, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание урока")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")
    image = models.ImageField(upload_to="lessons/", blank=True, null=True, verbose_name="Превью урока")
    video = models.FileField(upload_to="lessons/", blank=True, null=True, verbose_name="Видео урока")
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец урока",
    )

    def __str__(self):
        """
        Определяет отображение урока в админке.
        :return: Название урока и название курса
        """
        return f"{self.name} - {self.course.name}"

    class Meta:
        """
        Управляет поведением модели.
        Определяет имя модели в админке.
        """

        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
