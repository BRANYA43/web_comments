import pytest

from accounts.managers import UserManager
from accounts.models import User


@pytest.mark.django_db(transaction=True)
class TestUserManager:
    @pytest.fixture()
    def manager(self) -> UserManager:
        manager = UserManager()
        manager.model = User
        return manager

    def test_manager_creates_user(self, manager, test_email, test_username, test_password):
        assert User.objects.count() == 0

        user = manager.create_user(test_email, test_username, test_password)

        assert User.objects.count() == 1
        assert user.email == test_email
        assert user.username == test_username
        assert user.check_password(test_password) is True
        assert user.is_active is False
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_manager_creates_superuser(self, manager, test_email, test_username, test_password):
        assert User.objects.count() == 0

        user = manager.create_superuser(test_email, test_username, test_password)

        assert User.objects.count() == 1
        assert user.email == test_email
        assert user.username == test_username
        assert user.check_password(test_password) is True
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_manager_normalize_email_and_username_in_creation_time(self, manager, test_password):
        non_normalized_email = 'USER@TEST.COM'
        non_normalized_username = '𝕌𝑆𝗘𝖱𝒏𝒶𝗆𝐞𝟣𝟮𝟯𝟜'
        user = manager.create_user(non_normalized_email, non_normalized_username, test_password)
        assert user.email == 'USER@test.com'
        assert user.username == 'USERname1234'

    @pytest.mark.parametrize(
        'email,username,password',
        (
            ['', 'username1234', 'password1234'],
            ['username1234@test.com', '', 'password1234'],
            ['username1234@test.com', 'username1234', ''],
        ),
    )
    def test_manager_doesnt_create_user_if_email_or_username_or_password_isnt_supplied(
        self, manager, email, username, password
    ):
        assert User.objects.count() == 0

        with pytest.raises(ValueError, match='(Email|Username|Password) must be supplied.'):
            manager.create_user(email, username, password)

        assert User.objects.count() == 0
