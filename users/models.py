from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        max_length=500
    )

    display_name = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.username