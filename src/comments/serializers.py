from django.contrib.auth import get_user_model
from rest_framework import serializers  # NOQA

from comments.models import Comment

GeneralUser = get_user_model()


class UserSerializerField(serializers.ModelSerializer):
    class Meta:
        model = GeneralUser
        fields = ('email', 'username')
        read_only_fields = fields


class CommentListSerializer(serializers.ModelSerializer):
    user = UserSerializerField(read_only=True)

    class Meta:
        model = Comment
        fields = ('uuid', 'user', 'text', 'updated', 'created')
        read_only_fields = fields


class CommentRetrieveSerializer(serializers.ModelSerializer):
    user = UserSerializerField(read_only=True)

    class Meta:
        model = Comment
        fields = ('uuid', 'user', 'target', 'text', 'image', 'file', 'updated', 'created')
        read_only_fields = fields


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('user', 'target', 'text', 'image', 'file')


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text', 'image', 'file')
