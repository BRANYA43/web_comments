from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from django.test import override_settings
from django.utils.timezone import now

from comments.services import FileUploader


class TestFileUploader:
    uploader_class = FileUploader

    @pytest.fixture()
    def test_dir(self) -> str:
        return 'test_file_dir'

    @pytest.fixture()
    def test_instance(self) -> MagicMock:
        return MagicMock(uuid=uuid4())

    @pytest.fixture()
    def test_filename(self) -> str:
        return 'test_file.txt'

    def create_file(self, path: Path):
        path.parent.mkdir(parents=True)
        path.touch()

    def test_uploader_formats_path_if_it_has_datetime_value_to_format(self):
        path = 'dir/%Y/%m/%d'
        uploader = self.uploader_class(path)
        assert str(uploader._dir) == now().strftime(path)

    def test_uploader_returns_correct_path(self, test_dir, test_instance, test_filename):
        expected_filename = f'{test_instance.uuid}.{test_filename.split('.')[-1]}'
        expected_path = Path(test_dir, expected_filename)

        uploader = self.uploader_class(test_dir)
        path = uploader(test_instance, test_filename)

        assert path == expected_path

    def test_uploader_removes_old_existed_file_with_same_filename(
        self, test_dir, test_instance, test_filename, tmp_path
    ):
        tmp_media = tmp_path / 'test_media'
        with override_settings(MEDIA_ROOT=tmp_media):
            old_existed_file = tmp_media / test_dir / f'{test_instance.uuid}.{test_filename.split('.')[-1]}'
            self.create_file(old_existed_file)

            assert old_existed_file.exists() is True

            uploader = self.uploader_class(test_dir)
            uploader(test_instance, test_filename)

            assert old_existed_file.exists() is False
