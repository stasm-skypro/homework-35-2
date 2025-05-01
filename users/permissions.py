from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Разрешает владельцу полный доступ к объекту.
    Attributes:
        owner_field (str): Имя поля владельца
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, является ли текущий пользователь владельцем объекта.
        :param request: Запрос
        :param view:
        :param obj: Объект
        :return: True, если текущий пользователь авторизован и является владельцем, иначе False
        """
        return request.user.is_authenticated and obj.owner == request.user


class IsModerator(BasePermission):
    """
    Разрешает модератору все операции кроме create и destroy.
    Attributes:
        owner_field (str): Имя поля владельца
    """

    def has_permission(self, request, view):
        """
        Проверяет, является ли текущий пользователь модератором.
        :param request: Запрос
        :param view:
        :return: True, если текущий пользователь является модератором и действия create и destroy запрещены,
            иначе False
        """
        is_moderator = request.user.groups.filter(name="Модераторы").exists()
        return is_moderator and view.action not in ["create", "destroy"]

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, что модератор может просматривать и редактировать объект.
        :param request: Запрос
        :param view: Экземпляр представления
        :param obj: Объект
        :return: True, если пользователь является модератором, иначе False
        """
        return request.user.groups.filter(name="Модераторы").exists()


class DenyAll(BasePermission):
    """
    Полностью запрещает доступ.
    Attributes:
        owner_field (str): Имя поля владельца
    """

    def has_permission(self, request, view):
        """
        Запрещает доступ
        :param request: Запрос
        :param view: Экземпляр представления
        :return: False
        """
        return False


class IsProfileOwner(BasePermission):
    """
    Разрешает изменение только владельцу, но просмотр доступен всем авторизованным пользователям.
    Attributes:
        owner_field (str): Имя поля владельца
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, является ли текущий пользователь владельцем профиля.
        :param request: Запрос
        :param view: Экземпляр представления
        :param obj: Объект
        :return: True если текущий пользователь является владельцем, иначе False для всех операций. Если пользователь
        не является владельцем, то True для просмотра, иначе False
        """
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True  # Разрешаем просмотр профилей всем авторизованным
        return obj == request.user  # Разрешаем изменение только владельцу
