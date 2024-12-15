from django.contrib.auth import get_user_model
from django.shortcuts import render  # NOQA
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.serializers import Serializer

from rest_framework.viewsets import GenericViewSet


User = get_user_model()


class UserViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_classes: dict[str, Serializer] = {}
    permission_classes: dict[str, tuple[BasePermission]] = {
        'default': (AllowAny,),
    }

    def get_serializer_class(self) -> Serializer:
        return self.serializer_classes.get(self.action)

    def get_permissions(self) -> list[BasePermission]:
        if not (permission_classes := self.permission_classes.get(self.action)):
            permission_classes = self.permission_classes['default']
        return [permission() for permission in permission_classes]
