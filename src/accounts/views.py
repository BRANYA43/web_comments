from typing import Type

from django.contrib.auth import get_user_model
from django.shortcuts import render  # NOQA
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from rest_framework.viewsets import GenericViewSet

from accounts.serializers import LoginSerializer, RegisterSerializer

User = get_user_model()


class UserViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_classes: dict[str, Type[Serializer]] = {
        'login': LoginSerializer,
        'register': RegisterSerializer,
    }
    permission_classes: dict[str, tuple[Type[BasePermission]]] = {
        'default': (AllowAny,),
    }

    def get_serializer_class(self) -> Type[Serializer] | None:
        return self.serializer_classes.get(self.action)

    def get_permissions(self) -> list[BasePermission]:
        if not (permission_classes := self.permission_classes.get(self.action)):
            permission_classes = self.permission_classes['default']
        return [permission() for permission in permission_classes]

    @action(methods=['post'], detail=False)
    def login(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def register(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
