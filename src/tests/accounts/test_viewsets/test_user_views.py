import pytest
from pytest_lazy_fixtures import lf
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from accounts.serializers import UserRetrieveSerializer

GeneralUser = get_user_model()
pytestmark = pytest.mark.django_db(transaction=True)


class TestRetrieveView:
    url = reverse('user-retrieve-me')
    serializer_class = UserRetrieveSerializer

    def test_view_isnt_allowed_for_unauthenticated_user(self, api_client, test_user):
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_view_returns_expected_data(self, api_client, test_user):
        api_client.force_login(test_user)
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        expected_data = self.serializer_class(instance=test_user).data
        assert response.data == expected_data


class TestLogoutView:
    url = reverse('user-logout')

    def test_view_logs_user_out(self, api_client, test_user):
        api_client.force_login(test_user)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_view_doesnt_log_user_out_if_user_isnt_authenticated(self, api_client, test_user):
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestLoginView:
    url = reverse('user-login')

    @pytest.fixture()
    def test_data(self, test_email, test_password):
        return dict(
            email=test_email,
            password=test_password,
        )

    def test_view_logs_user_in(self, api_client, test_data, test_user):
        response = api_client.post(self.url, data=test_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'email': test_user.email, 'username': test_user.username}

    @pytest.mark.parametrize(
        'data',
        [
            {},
            {'email': '', 'password': ''},
            {'email': lf('test_email'), 'password': ''},
            {'email': '', 'password': lf('test_password')},
        ],
    )
    def test_view_doesnt_log_user_in_if_credentials_are_empty(self, api_client, data, test_user):
        response = api_client.post(self.url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        'data',
        [
            {'email': 'invalidEmail@test.com', 'password': 'invalidPassword1234'},
            {'email': lf('test_email'), 'password': 'invalidPassword1234'},
            {'email': 'invalidEmail@test.com', 'password': lf('test_password')},
        ],
    )
    def test_view_doesnt_log_user_in_if_no_user_doesnt_exist_with_such_credentials(self, api_client, data, test_user):
        response = api_client.post(self.url, data=data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_view_doesnt_log_user_in_if_user_isnt_active(self, api_client, test_data, test_user):
        test_user.is_active = False
        test_user.save()

        response = api_client.post(self.url, data=test_data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN


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
        assert user.is_active is True
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
