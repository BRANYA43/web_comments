from django.contrib.auth import get_user_model
from rest_framework import serializers  # NOQA

GeneralUser = get_user_model()


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
