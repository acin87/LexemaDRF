from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import F

from lexema_friends.models import Friend
from lexema_post.models import Post


@receiver(pre_save, sender=Friend)
def track_friendship_status(sender, instance, **kwargs):
    """Запоминаем предыдущий статус перед сохранением"""
    if instance.pk:
        try:
            instance._previous_status = Friend.objects.get(pk=instance.pk).status
        except Friend.DoesNotExist:
            instance._previous_status = None


@receiver(post_save, sender=Friend)
def handle_friend_notification(sender, instance, created, **kwargs):
    """Обработчик уведомлений для всех сценариев"""
    if created:
        # Новый запрос в друзья
        instance.send_notification(Friend.Status.PENDING)
    else:
        # Проверяем изменение статуса
        current_status = instance.status
        previous_status = getattr(instance, "_previous_status", None)

        if previous_status != current_status:
            # Статус изменился - отправляем уведомление
            instance.send_notification(current_status)

            # Дополнительное уведомление при принятии дружбы
            if current_status == Friend.Status.ACCEPTED:
                instance.send_accept_notification()


@receiver(post_save, sender=Post)
def handle_post_notification(sender, instance, created, **kwargs):
    if created:
        # Отправляем уведомление о новом посте
        instance.send_notification()
