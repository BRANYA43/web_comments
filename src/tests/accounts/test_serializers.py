from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_lazy_fixtures import lf
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.test import RequestFactory

from accounts.serializers import RegisterSerializer, LoginSerializer

GeneralUser = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestLoginSerializer:
    serializer_class = LoginSerializer

    @pytest.fixture()
    def test_data(self, test_email, test_password):
        return dict(
            email=test_email,
            password=test_password,
        )

    @pytest.fixture()
    def test_request(self):
        factory = RequestFactory()
        request_ = factory.get('/404/')
        request_.user = AnonymousUser()
        request_.session = MagicMock()
        return request_

    def test_serializer_logs_user_in(self, test_data, test_user, test_request):
        assert test_request.user.is_authenticated is False

        serializer = self.serializer_class(data=test_data, context={'request': test_request})
        serializer.is_valid(raise_exception=True)  # not raise

        assert test_request.user.is_authenticated is True
        assert test_request.user == test_user

    @pytest.mark.parametrize(
        'data',
        [
            {},
            {'email': '', 'password': ''},
            {'email': lf('test_email'), 'password': ''},
            {'email': '', 'password': lf('test_password')},
        ],
    )
    def test_serializer_doesnt_log_user_in_if_credentials_are_empty(self, data, test_user, test_request):
        assert test_request.user.is_authenticated is False

        serializer = self.serializer_class(data=data, context={'request': test_request})

        pytest.raises(ValidationError, serializer.is_valid, raise_exception=True)
        assert test_request.user.is_authenticated is False

    @pytest.mark.parametrize(
        'data',
        [
            {'email': 'invalidEmail@test.com', 'password': 'invalidPassword1234'},
            {'email': lf('test_email'), 'password': 'invalidPassword1234'},
            {'email': 'invalidEmail@test.com', 'password': lf('test_password')},
        ],
    )
    def test_serializer_doesnt_log_user_in_if_no_user_doesnt_exist_with_such_credentials(
        self, data, test_user, test_request
    ):
        assert test_request.user.is_authenticated is False

        serializer = self.serializer_class(data=data, context={'request': test_request})

        pytest.raises(AuthenticationFailed, serializer.is_valid, raise_exception=True)
        assert test_request.user.is_authenticated is False

    def test_serializer_doesnt_log_user_in_if_user_isnt_active(self, test_data, test_user, test_request):
        test_user.is_active = False
        test_user.save()

        assert test_request.user.is_authenticated is False

        serializer = self.serializer_class(data=test_data, context={'request': test_request})

        pytest.raises(AuthenticationFailed, serializer.is_valid, raise_exception=True)
        assert test_request.user.is_authenticated is False


class TestRegistrationSerializer:
    serializer_class = RegisterSerializer

    @pytest.fixture()
    def test_data(self, test_email, test_username, test_password) -> dict[str, Any]:
        return dict(
            email=test_email,
            username=test_username,
            password=test_password,
            confirming_password=test_password,
        )

    @pytest.mark.django_db(transaction=True)
    def test_serializer_creates_user(self, test_data):
        assert GeneralUser.objects.count() == 0

        serializer = self.serializer_class(data=test_data)
        serializer.is_valid(raise_exception=True)  # not raise
        user = serializer.save()

        assert GeneralUser.objects.count() == 1
        assert user.email == test_data['email']
        assert user.username == test_data['username']
        assert user.check_password(test_data['password']) is True

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        'password,confirming_password',
        [
            ('', ''),
            ('password1234', ''),
            ('', 'password1234'),
        ],
    )
    def test_serializer_doesnt_create_user_if_one_of_password_isnt_supplied(
        self, test_email, test_username, password, confirming_password
    ):
        data = dict(
            email=test_email,
            username=test_username,
            password=password,
            confirming_password=confirming_password,
        )

        assert GeneralUser.objects.count() == 0

        with pytest.raises(ValidationError, match='(password|confirming_password).+This field may not be blank.'):
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)

        assert GeneralUser.objects.count() == 0

    @pytest.mark.django_db(transaction=True)
    def test_serializer_doesnt_create_user_if_passwords_dont_match(self, test_data):
        test_data['password'] = 'unmatch_password1234'

        assert GeneralUser.objects.count() == 0

        with pytest.raises(ValidationError, match=self.serializer_class.default_error_messages['passwords_unmatch']):
            serializer = self.serializer_class(data=test_data)
            serializer.is_valid(raise_exception=True)

        assert GeneralUser.objects.count() == 0

    def test_password_fields_is_write_only(self):
        serializer = self.serializer_class()
        assert serializer.fields['password'].write_only is True
        assert serializer.fields['confirming_password'].write_only is True
