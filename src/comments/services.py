from pathlib import Path

from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class FileUploader:
    def __init__(self, dir: Path | str, /):
        self._dir = Path(dir)
        self._media_root = settings.MEDIA_ROOT

    def __call__(self, filename: str, instance, *args, **kwargs):
        new_filename = self._get_new_filename(filename, instance)
        path = self._dir / new_filename
        full_path = self._media_root / path
        if full_path.exists():
            full_path.unlink()
        return path

    def _get_new_filename(self, filename: str, instance) -> str:
        extension = filename.split('.')[-1]
        return f'{instance.uuid}.{extension}'
