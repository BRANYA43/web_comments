import django_filters

from comments.models import Comment


class CommentFilter(django_filters.FilterSet):
    target_is_null = django_filters.BooleanFilter(field_name='target', lookup_expr='isnull')
    target = django_filters.UUIDFilter(field_name='target__uuid', lookup_expr='exact')

    ordering = django_filters.OrderingFilter(
        fields=(
            ('user__email', 'email'),
            ('user__username', 'username'),
            ('updated', 'updated'),
            ('created', 'created'),
        ),
        field_labels={
            'user__emai': 'Email',
            'user__username': 'Username',
            'updated': 'Date of update',
            'created': 'Date of creation',
        },
    )

    class Meta:
        model = Comment
        fields = ['target', 'target_is_null']
