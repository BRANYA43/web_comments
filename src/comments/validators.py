from typing import Literal

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class ImageSizeValidator:
    default_message_errors = {'image_too_large': 'Image must have {width}x{height} size.'}

    def __init__(self, width: int, height: int):
        self._width = int(width)
        self._height = int(height)

    def __call__(self, value, *args, **kwargs):
        if value.width > self._width or value.height > self._height:
            raise ValidationError(
                self.default_message_errors['image_too_large'].format(width=self._width, height=self._height),
                'image_too_large',
            )


@deconstructible
class FileSizeValidator:
    _coefficients = {
        'b': 1,
        'kb': 1024,
    }

    default_message_errors = {'file_too_large': 'File size must be less or equal {max_size}{unit}.'}

    def __init__(self, max_size: int, unit: Literal['b', 'kb']):
        self._max_size = int(max_size)
        self._unit = str(unit)
        try:
            self._max_size_in_bytes = self._max_size * self._coefficients[str(unit)]
        except KeyError:
            raise ValueError(f'Unit must be one of next values: {self._coefficients.keys()}')

    def __call__(self, value, *args, **kwargs):
        if value.size > self._max_size_in_bytes:
            raise ValidationError(
                self.default_message_errors['file_too_large'].format(max_size=self._max_size, unit=self._unit),
                'file_too_large',
            )
