import logging
from datetime import timedelta
from django.utils import timezone

from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER
from materials.models import Course


logger = logging.getLogger(__name__)


@shared_task
def send_course_update_email(course_id):
    """
    Отправляет уведомление об обновлении курса.
    :param course_id: id курса
    :return: None
    """
    from users.models import Subscription  # локальный импорт для избежания циклов

    try:  # Если курс с таким id не существует, то ничего не делаем
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return

    # Если с момента последнего обновления прошло менее 4 часов, то ничего не делаем
    now = timezone.now()
    if now - course.updated_at < timedelta(hours=4):
        return

    # Отправляем уведомление
    subject = "Обновление курса: %s" % course.name
    message = "Материалы курса «%s» были обновлены.\n\nОписание: %s" % (
        course.name,
        course.description,
    )
    subscribers = Subscription.objects.filter(course=course).select_related("user")
    for sub in subscribers:
        if sub.user.email:
            send_mail(
                subject=subject,
                message=message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[sub.user.email],
                fail_silently=True,
            )
            logger.info("Письмо отправлено пользователю %s" % sub.user)
