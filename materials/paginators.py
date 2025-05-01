from rest_framework.pagination import PageNumberPagination


class CoursePagination(PageNumberPagination):
    """
    Определяет пагинацию для представления курсов.
    """

    page_size = 2  # Количество элементов на одной странице
    page_size_query_param = "page_size"  # Позволяет клиенту запрашивать разное количество элементов
    max_page_size = 10  # Максимальное количество элементов на одной странице


class LessonPagination(PageNumberPagination):
    """
    Определяет пагинацию для представления уроков.
    """

    page_size = 2  # Количество элементов на одной странице
    page_size_query_param = "page_size"  # Позволяет клиенту запрашивать разное количество элементов
    max_page_size = 10  # Максимальное количество элементов на одной странице
