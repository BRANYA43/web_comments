from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError

from comments.validators import FileSizeValidator


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
