"""
Тут есть проблема: код выполняется сразу при импорте файла, а не в ответ на какое-то событие (например, создание
пользователя, запуск проекта и т.д.). То есть, каждый раз при старте Django-сервера или при любой миграции этот код
будет выполняться, что не всегда правильно.

В signals.py обычно пишут функции, которые реагируют на сигналы, например:
post_save
post_migrate
pre_save и др.

Это не было учтено сразу при написании кода. Код запускается вместе с проектом и вызывает задачу
users.tasks.block_inactive_users, которая блокирует пользователя, если тот уже более 30 дней не заходил в учётку.

Непонятно к чему привязать signal. Запускаться задача должна сразу после запуска проекта и чекать пользователей
1 раз в день. Поэтому привяжемся к сигналу post_migrate.
"""


from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json


@receiver(post_migrate)
def create_block_inactive_users_task(sender, **kwargs):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.DAYS,
    )

    PeriodicTask.objects.get_or_create(
        name="Block inactive users",  # ищем по имени!
        defaults={
            "interval": schedule,
            "task": "users.tasks.block_inactive_users",
            "kwargs": json.dumps({}),
        },
    )
