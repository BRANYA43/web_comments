from pathlib import Path

from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now


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
