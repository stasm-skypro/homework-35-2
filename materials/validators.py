import re

from rest_framework import serializers


class DescriptionValidator:
    """
    Определяет валидацию описания урока.
    """

    def __init__(self, field):
        """
        :param field: Поле модели, которое нужно валидировать
        :return: None
        """
        self.field = field

    def __call__(self, value):
        """
        :param value: Словарь с полями модели
        :return: None
        """
        pattern = re.compile(r"(?:https?://)?(?:www\.)?(youtube\.com|youtu\.be)")  # Проверяет также сокращённые ссылки

        field_to_validate = str(dict(value).get(self.field))
        if "https://" in field_to_validate or "http://" in field_to_validate:
            if not pattern.match(field_to_validate):
                raise serializers.ValidationError("Ссылка на другие каналы кроме youtube не допустима.")
