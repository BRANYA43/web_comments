from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError

from comments.validators import FileSizeValidator, ImageSizeValidator, HTMLTagValidator


class TestHTMLTagValidator:
    validator = HTMLTagValidator(['div', 'a', 'p', 'strong'], ['br'])

    valid_html = """
    <div class="div-class"><p>Hello <strong>World</strong><br><a href="#">Cool Link</a></p></div>
    """
    html_has_forbidden_tags = f"""
    {valid_html}<script src="hack_script.js">alert(HACK!!!);</script>
    """

    def test_validator_doesnt_raise_error_for_valid_html(self):
        self.validator(self.valid_html)  # not raise

    def test_validator_raises_error_for_html_has_forbidden_tags(self):
        with pytest.raises(ValidationError, match='Text has forbidden tags.'):
            self.validator(self.html_has_forbidden_tags)

    @pytest.mark.parametrize('html', ['<a>', '</a>'])
    def test_validator_raises_error_for_html_has_not_closed_tag(self, html):
        with pytest.raises(ValidationError, match='Text has not closed tags.'):
            self.validator(html)


class TestImageSizeValidator:
    validator_class = ImageSizeValidator

    @pytest.mark.parametrize('width, height', [(25, 100), (50, 150), (100, 200)])
    def test_validator_doesnt_raise_error_to_valid_width_or_height(self, width, height):
        validator = self.validator_class(100, 200)
        validator(MagicMock(width=width, height=height))  # not raise

    @pytest.mark.parametrize('width, height', [(100, 200), (200, 150), (200, 200)])
    def test_validator_raises_error_to_invalid_width_or_height(self, width, height):
        validator = self.validator_class(100, 150)
        with pytest.raises(ValidationError, match='Image must have 100x150 size.'):
            validator(MagicMock(width=width, height=height))


class TestFileSizeValidator:
    validator_class = FileSizeValidator

    @pytest.mark.parametrize('file', [MagicMock(size=i) for i in range(1, 6)])
    def test_validator_doesnt_raise_error_to_valid_size_in_bytes(self, file):
        validator = self.validator_class(5, 'b')
        validator(file)  # not raise

    @pytest.mark.parametrize('file', [MagicMock(size=i * 1024) for i in range(1, 6)])
    def test_validator_doesnt_raise_error_to_valid_size_in_kb(self, file):
        validator = self.validator_class(5, 'kb')
        validator(file)  # not raise

    @pytest.mark.parametrize('file', [MagicMock(size=i) for i in range(6, 11)])
    def test_validator_raises_error_for_too_large_size_in_bytes(self, file):
        validator = self.validator_class(5, 'b')
        with pytest.raises(ValidationError, match='File size must be less or equal 5b.'):
            validator(file)

    @pytest.mark.parametrize('file', [MagicMock(size=i * 1024) for i in range(6, 11)])
    def test_validator_raises_error_for_too_large_size_in_kb(self, file):
        validator = self.validator_class(5, 'kb')
        with pytest.raises(ValidationError, match='File size must be less or equal 5kb.'):
            validator(file)

    @pytest.mark.parametrize('invalid_unit', ['', 1, 1.1, None, 'None', 'bbb'])
    def test_validator_raises_error_for_invalid_unit(self, invalid_unit):
        with pytest.raises(ValueError, match='Unit must be one of next values:'):
            self.validator_class(1, invalid_unit)

    @pytest.mark.parametrize('invalid_size', ['', None, object, 'a'])
    def test_validator_raises_error_for_invalid_max_size(self, invalid_size):
        with pytest.raises((TypeError, ValueError)):
            self.validator_class(invalid_size, 'b')
