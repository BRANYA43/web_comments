from django.contrib.auth import get_user_model, authenticate, login
from rest_framework import serializers  # NOQA
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed

GeneralUser = get_user_model()


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralUser
        fields = ('email', 'username')
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._request = kwargs['context']['request']
        self._cached_user = None

    @property
    def cached_user(self):
        return self._cached_user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email and not password:
            raise NotAuthenticated

        self._cached_user = authenticate(self._request, username=email, password=password)

        if not self._cached_user:
            raise AuthenticationFailed

        login(self._request, self._cached_user)

        return {'email': self._cached_user.email, 'username': self._cached_user.username}


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=True)
    confirming_password = serializers.CharField(write_only=True, required=True, trim_whitespace=True)

    default_error_messages = {
        'passwords_unmatch': 'Password and confirming password must match.',
    }

    class Meta:
        model = GeneralUser
        fields = ('email', 'username', 'password', 'confirming_password')

    def validate(self, data: dict):
        password_1 = data.get('password')
        password_2 = data.get('confirming_password')
        if password_1 and password_2:
            if password_1 != password_2:
                raise serializers.ValidationError(
                    detail=self.default_error_messages['passwords_unmatch'],
                    code='passwords_unmatch',
                )

        return data

    def create(self, validated_data):
        validated_data.pop('confirming_password')
        return GeneralUser.objects.create_user(**validated_data)
