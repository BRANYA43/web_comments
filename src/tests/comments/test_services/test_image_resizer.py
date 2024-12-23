import pytest
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

from comments.services import resize_image


class TestImageResizer:
    @pytest.fixture()
    def test_valid_image(self):
        img = Image.new('RGB', (300, 200), color='green')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        return InMemoryUploadedFile(
            buffer,
            None,
            'test_image.jpg',
            'image/jpeg',
            buffer.getbuffer().nbytes,
            None,
        )

    @pytest.fixture
    def test_large_image(self):
        img = Image.new('RGB', (1000, 1000), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        return InMemoryUploadedFile(
            buffer,
            None,
            'test_image.jpg',
            'image/jpeg',
            buffer.getbuffer().nbytes,
            None,
        )

    def test_service_doesnt_resize_image_for_valid_image(self, test_valid_image):
        width = 320
        height = 240
        resized_image = resize_image(test_valid_image, width, height)

        assert resized_image is test_valid_image

    def test_service_resizes_image_for_large_image(serf, test_large_image):
        width = 320
        height = 240
        resized_image = resize_image(test_large_image, width, height)
        img = Image.open(resized_image.file)

        assert img.size[0] <= width
        assert img.size[1] <= height
        assert img.size[0] == img.size[1]
