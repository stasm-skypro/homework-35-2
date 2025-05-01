from users.models import User
from celery import shared_task
from datetime import timedelta
from django.utils import timezone


@shared_task
def block_inactive_users(user_id):
    """
    Блокирует всех пользователей, которые не входили в аккаунт более месяца.
    :param user_id: id пользователя
    :return: None
    """
    month_ago = timezone.now() - timedelta(days=30)
    users_to_block = User.objects.filter(is_active=True, last_login__lt=month_ago)  # Выбираем тех пользователей,
    # которые не входили в аккаунт более месяца

    for user in users_to_block:
        user.is_active = False
        user.save()
