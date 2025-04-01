from django.db.models.signals import post_delete
from django.dispatch import receiver

from lexema_post.models import PostImage

@receiver(post_delete, sender=PostImage)
def delete_post_image_file(sender, instance, **kwargs):
    """Удаляет файл изображения при удалении записи PostImage"""
    if instance.image:
        instance.image.delete(save=False)
