from typing import Any

import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from accounts.serializers import RegisterSerializer

GeneralUser = get_user_model()


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
