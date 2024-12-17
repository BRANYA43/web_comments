from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from comments.models import Comment


@pytest.mark.django_db(transaction=True)
class TestComment:
    def get_datetime_path(self) -> str:
        return now().strftime('/%Y/%m/%d/')

    @pytest.fixture()
    def expected_image_path(self):
        return Path('comments/images/', self.get_datetime_path())

    @pytest.fixture()
    def expected_file_path(self):
        return Path('comments/files/', self.get_datetime_path())

    @pytest.fixture()
    def test_data(self, test_user):
        return {'user': test_user, 'text': 'a'}

    def test_creating(self, test_user):
        comment = Comment.objects.create(user=test_user, text='a' * 2048)
        comment.full_clean()  # not raise

    def test_text_cannot_be_great_than_2048_chars(self, test_user):
        with pytest.raises(ValidationError):
            comment = Comment.objects.create(user=test_user, text='a' * 2049)
            comment.full_clean()

    def test_file_is_saved_in_expected_path(self, test_media_root, test_data, test_file, expected_file_path):
        comment = Comment.objects.create(**test_data, file=test_file)
        comment.full_clean()  # not raise

        assert str(expected_file_path) in comment.file.path

    def test_file_isnt_saved_if_its_size_is_great_than_100kb(self, test_media_root, test_data, test_large_file):
        with pytest.raises(ValidationError):
            comment = Comment.objects.create(**test_data, file=test_large_file)
            comment.full_clean()

    def test_file_isnt_saved_for_invalid_extension(self, test_media_root, test_data, test_invalid_extension_file):
        with pytest.raises(ValidationError):
            comment = Comment.objects.create(**test_data, file=test_invalid_extension_file)
            comment.full_clean()

    def test_image_is_saved_in_expected_path(self, test_media_root, test_data, test_image, expected_image_path):
        comment = Comment.objects.create(**test_data, image=test_image)

        assert str(expected_image_path) in comment.image.path

    def test_image_isnt_saved_if_its_size_is_great_than_300kb(self, test_media_root, test_data, test_large_image):
        with pytest.raises(ValidationError):
            comment = Comment.objects.create(**test_data, image=test_large_image)
            comment.full_clean()

    def test_image_isnt_saved_if_its_width_and_height_are_great_than_320x240(
        self, test_media_root, test_data, test_large_wh_image
    ):
        with pytest.raises(ValidationError):
            comment = Comment.objects.create(**test_data, image=test_large_wh_image)
            comment.full_clean()

    def test_image_isnt_saved_for_invalid_extension(self, test_media_root, test_data, test_invalid_extension_image):
        with pytest.raises(ValidationError):
            comment = Comment.objects.create(**test_data, image=test_invalid_extension_image)
            comment.full_clean()
