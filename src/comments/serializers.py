from rest_framework import serializers  # NOQA

from comments.models import Comment


class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('uuid', 'user', 'text', 'updated', 'created')
        read_only_fields = fields


class CommentRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('uuid', 'user', 'target', 'text', 'image', 'file', 'updated', 'created')
        read_only_fields = fields
