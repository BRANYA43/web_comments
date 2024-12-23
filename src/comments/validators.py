from html.parser import HTMLParser
from itertools import chain
from typing import Literal, Sequence

import PIL.Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.deconstruct import deconstructible


class HTMLParserForValidator(HTMLParser):
    def __init__(self, allowed_tags: Sequence[str], allowed_single_tags: Sequence[str], **kwargs):
        super().__init__(**kwargs)
        self._allowed_tags = list(allowed_tags)
        self._allowed_single_tags = list(allowed_single_tags)
        self._parsed_start_tags: list[str] = []
        self._found_forbidden_tags: list[str] = []
        self._found_not_closed_tags: list[str] = []

    @property
    def found_forbidden_tags(self):
        return self._found_forbidden_tags.copy()

    @property
    def found_not_closed_tags(self):
        return self._found_not_closed_tags.copy()

    def handle_starttag(self, tag, attrs):
        if tag not in chain(self._allowed_tags, self._allowed_single_tags):
            self._found_forbidden_tags.append(tag)
        if tag not in self._allowed_single_tags:
            self._parsed_start_tags.append(tag)

    def handle_endtag(self, tag):
        if self._parsed_start_tags and self._parsed_start_tags[-1] == tag:
            self._parsed_start_tags.pop()
        else:
            if tag in self._allowed_tags:
                self._found_not_closed_tags.append(tag)

    def close(self):
        super().close()
        if self._parsed_start_tags:
            self._found_not_closed_tags += self._parsed_start_tags


@deconstructible
class HTMLTagValidator:
    default_message_errors = {
        'not_allowed_tags': 'Text has forbidden tags.',
        'not_closed_tags': 'Text has not closed tags.',
    }

    def __init__(
        self, allowed_tags: Sequence[str], allowed_single_tags: Sequence[str], parser_class=HTMLParserForValidator
    ):
        self._parser_class = parser_class
        self._allowed_tags = allowed_tags
        self._allowed_single_tags = allowed_single_tags

    def __call__(self, value, *args, **kwargs):
        parser = self._parser_class(self._allowed_tags, self._allowed_single_tags)
        parser.feed(value)
        parser.close()

        if parser.found_forbidden_tags:
            raise ValidationError(
                self.default_message_errors['not_allowed_tags'],
                'not_allowed_tags',
            )

        if parser.found_not_closed_tags:
            raise ValidationError(
                self.default_message_errors['not_closed_tags'],
                'not_closed_tags',
            )


@deconstructible
class ImageSizeValidator:
    default_message_errors = {'image_too_large': 'Image must have {width}x{height} size.'}

    def __init__(self, width: int, height: int):
        self._width = int(width)
        self._height = int(height)

    def __call__(self, value, *args, **kwargs):
        if isinstance(value, InMemoryUploadedFile):
            value = PIL.Image.open(value.file)
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
