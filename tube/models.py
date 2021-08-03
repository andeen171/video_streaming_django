from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.validators import FileExtensionValidator


class Tag(models.Model):
    name = models.CharField(max_length=255)


class Video(models.Model):
    extensions = ['mp4', 'avi', 'wav', 'mov', 'webm']
    title = models.CharField(max_length=255)
    file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=extensions)])
    upload_date = models.DateTimeField(default=now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)

    class meta:
        ordering = ['upload_date']


class VideoTag(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
