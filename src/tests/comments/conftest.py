from io import BytesIO

import PIL.Image
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.accounts.conftest import test_user, test_email, test_password, test_username  # NOQA


def get_uploaded_file(name='test_file.txt', size=1, content=b'a', content_type='text/plain') -> SimpleUploadedFile:
    content = content * size
    return SimpleUploadedFile(name=name, content=content, content_type=content_type)


def get_uploaded_image(
    name='test_image.png', content_type='image/png', format='PNG', width=320, height=240, extra_size=0
) -> SimpleUploadedFile:
    image = PIL.Image.new('RGB', (width, height), color='blue')
    image_bytes = BytesIO()
    image.save(image_bytes, format=format)
    image_bytes.seek(0)
    extra_content = b'0' * extra_size if extra_size > 0 else b''
    return SimpleUploadedFile(name=name, content=image_bytes.read() + extra_content, content_type=content_type)


@pytest.fixture()
def test_file() -> SimpleUploadedFile:
    return get_uploaded_file()


@pytest.fixture()
def test_large_file() -> SimpleUploadedFile:
    return get_uploaded_file('test_large_file.txt', size=101 * 1024)


@pytest.fixture()
def test_invalid_extension_file() -> SimpleUploadedFile:
    return get_uploaded_file('test_invalid_extension_file.pdf')


@pytest.fixture()
def test_image() -> SimpleUploadedFile:
    return get_uploaded_image()


@pytest.fixture()
def test_large_image() -> SimpleUploadedFile:
    return get_uploaded_image(name='test_large_image.png', extra_size=301 * 1024)


@pytest.fixture()
def test_large_wh_image() -> SimpleUploadedFile:
    return get_uploaded_image(name='test_large_image.png', extra_size=301 * 1024, width=1024, height=1024)


@pytest.fixture()
def test_invalid_extension_image() -> SimpleUploadedFile:
    return get_uploaded_image(name='test_large_image.bmp', format='BMP', content_type='image/bmp')
