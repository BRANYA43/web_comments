import factory.django
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from pytest_factoryboy import register
from rest_framework.test import APIClient


GeneralUser = get_user_model()


########################################################################################################################
# Factories
########################################################################################################################
@register
class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Faker('email')
    username = factory.Faker('user_name')
    password = factory.django.Password('password1234')

    class Meta:
        model = GeneralUser


########################################################################################################################
# Fixtures
########################################################################################################################
@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def test_media_root(tmp_path):
    path = tmp_path / 'test_media'
    with override_settings(MEDIA_ROOT=path):
        yield path
