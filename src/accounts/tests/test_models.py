import pytest
from django.conf import settings

from accounts.models import User


class TestUserModel:
    @pytest.mark.django_db(transaction=True)
    def test_creating(self, test_email, test_username, test_password):
        user = User.objects.create(email=test_email, username=test_username, password=test_password)
        user.full_clean()  # not raise

    def test_username_and_email_fields_is_set_as_email(self):
        assert User.USERNAME_FIELD == 'email'
        assert User.EMAIL_FIELD == 'email'

    def test_username_is_added_to_required_fields(self):
        assert User.REQUIRED_FIELDS == ['username']

    def test_user_model_is_set_as_auth_user_model_in_settings(self):
        assert settings.AUTH_USER_MODEL == 'accounts.User'
