import pytest
from rest_framework.test import APIClient

from accounts.models import User


@pytest.fixture()
def test_email() -> str:
    return 'rick.sanchez@test.com'


@pytest.fixture()
def test_username() -> str:
    return 'rick'


@pytest.fixture()
def test_password() -> str:
    return 'rick1234'


@pytest.fixture()
def test_user(test_email, test_username, test_password) -> User:
    return User.objects.create_user(email=test_email, username=test_username, password=test_password, is_active=True)


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()
