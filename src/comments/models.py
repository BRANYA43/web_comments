from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, FileExtensionValidator
from django.db import models  # NOQA

from comments.services import FileUploader
from comments.validators import FileSizeValidator, ImageSizeValidator, HTMLTagValidator

GeneralUser = get_user_model()


class Comment(models.Model):
    uuid = models.UUIDField(
        default=uuid4,
        primary_key=True,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(
        to=GeneralUser,
        on_delete=models.PROTECT,
    )
    target = models.ForeignKey(
        to='Comment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='answers',
    )
    text = models.TextField(
        validators=[
            MaxLengthValidator(2048),
            HTMLTagValidator(['p', 'strong', 'em', 'u', 's', 'code', 'a'], ['br']),
        ],
    )
    image = models.ImageField(
        upload_to=FileUploader('comments/images/%Y/%m/%d/'),
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(['png', 'jpg', 'gif']),
            FileSizeValidator(300, 'kb'),
            ImageSizeValidator(320, 240),
        ],
    )
    file = models.FileField(
        upload_to=FileUploader('comments/files/%Y/%m/%d/'),
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(['txt']),
            FileSizeValidator(100, 'kb'),
        ],
    )
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']
