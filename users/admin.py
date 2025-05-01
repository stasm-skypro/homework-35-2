from django.contrib import admin

from users.models import User, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Отображает поля модели Пользователи в админке.
    """

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("username",)
    search_fields = (
        "username",
        "email",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Отображает поля модели Оплаты в админке.
    """

    list_display = (
        "user",
        "course",
        "lesson",
        "payment_method",
        "amount",
        "date",
    )
    list_filter = (
        "user",
        "course",
        "lesson",
        "payment_method",
    )
    search_fields = (
        "user__email",
        "course__name",
        "lesson__name",
    )
