import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def test_media_root(tmp_path):
    path = tmp_path / 'test_media'
    with override_settings(MEDIA_ROOT=path):
        yield path
