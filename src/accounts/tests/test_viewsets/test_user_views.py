import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse


GeneralUser = get_user_model()
pytestmark = pytest.mark.django_db(transaction=True)


class TestRegisterView:
    url = reverse('user-register')

    @pytest.fixture()
    def test_data(self, test_email, test_username, test_password):
        return dict(
            email=test_email,
            username=test_username,
            password=test_password,
            confirming_password=test_password,
        )

    def test_view_registers_user(self, api_client, test_data):
        assert GeneralUser.objects.count() == 0

        response = api_client.post(self.url, data=test_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data is None
        assert GeneralUser.objects.count() == 1
        user = GeneralUser.objects.first()

        assert user.email == test_data['email']
        assert user.username == test_data['username']
        assert user.check_password(test_data['password']) is True
        assert user.is_active is False
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_view_doesnt_register_user_if_user_with_credentials_exists(self, api_client, test_data, test_user):
        assert GeneralUser.objects.count() == 1

        response = api_client.post(self.url, data=test_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert GeneralUser.objects.count() == 1

    def test_view_doesnt_register_user_if_passwords_dont_match(self, api_client, test_data):
        test_data['password'] = 'unmatch_password1234'
        assert GeneralUser.objects.count() == 0

        response = api_client.post(self.url, data=test_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert GeneralUser.objects.count() == 0
