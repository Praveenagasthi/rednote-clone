from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Post


@receiver(pre_delete, sender=Post)
def delete_post_images(sender, instance, **kwargs):
    for post_image in instance.images.all():
        if post_image.image:
            post_image.image.delete(save=False)