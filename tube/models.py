from django.db import models
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(max_length=255)


class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)


class VideoTag(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
