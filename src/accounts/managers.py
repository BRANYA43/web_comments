from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email: str, username: str, password: str, **extra_fields):
        extra_fields['is_active'] = False
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email: str, username: str, password: str, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        return self._create_user(email, username, password, **extra_fields)

    def _create_user(self, email: str, username: str, password: str, **extra_fields):
        if not email:
            raise ValueError('Email must be supplied.')

        if not username:
            raise ValueError('Username must be supplied.')

        if not password:
            raise ValueError('Password must be supplied.')

        user = self.model(
            email=self.normalize_email(email),
            username=self.model.normalize_username(username),
            **extra_fields,
        )
        user.set_password(password)
        user.save()

        return user
