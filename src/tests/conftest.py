import factory.django
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from pytest_factoryboy import register
from rest_framework.request import Request
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from comments.models import Comment

GeneralUser = get_user_model()


########################################################################################################################
# Factories
########################################################################################################################
@register
@register(_name='owner')
@register(_name='not_owner')
class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Faker('email')
    username = factory.Faker('user_name')
    password = factory.django.Password('password1234')

    class Meta:
        model = GeneralUser


@register
class CommentFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    text = factory.Faker('text')

    class Meta:
        model = Comment


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


@pytest.fixture()
def test_request() -> Request:
    return APIRequestFactory().get('/')
