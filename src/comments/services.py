from io import BytesIO
from pathlib import Path

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now


def resize_image(uploaded_image: InMemoryUploadedFile, width=320, height=240) -> InMemoryUploadedFile:
    uploaded_image.seek(0)
    image = Image.open(uploaded_image.file)
    if image.width > width or image.height > height:
        ratio = min(float(width) / image.size[0], float(height) / image.size[1])
        w = int(image.size[0] * ratio)
        h = int(image.size[1] * ratio)
        resized_image = image.resize((w, h), Image.Resampling.LANCZOS)

        buffer = BytesIO()
        resized_image.save(buffer, format=image.format)
        buffer.seek(0)

        resized_uploaded_image = InMemoryUploadedFile(
            file=buffer,
            field_name=uploaded_image.field_name,
            name=uploaded_image.name,
            content_type=uploaded_image.content_type,
            size=buffer.getbuffer().nbytes,
            charset=uploaded_image.charset,
        )
        return resized_uploaded_image
    uploaded_image.seek(0)
    return uploaded_image


@deconstructible
class FileUploader:
    def __init__(self, dir: Path | str, /):
        self._dir = Path(self._format_datetime_in_path(dir))
        self._media_root = settings.MEDIA_ROOT

    def __call__(self, instance, filename: str, *args, **kwargs):
        new_filename = self._get_new_filename(filename, instance)
        path = self._dir / new_filename
        full_path = self._media_root / path
        if full_path.exists():
            full_path.unlink()
        return path

    def _get_new_filename(self, filename: str, instance) -> str:
        extension = filename.split('.')[-1]
        return f'{instance.uuid}.{extension}'

    def _format_datetime_in_path(self, path) -> str:
        return now().strftime(path)
