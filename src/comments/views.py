from typing import Type

from django.shortcuts import render  # NOQA
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from comments.filters import CommentFilter
from comments.models import Comment
from comments.paginators import PageNumberPaginator
from comments.permissions import IsOwner
from comments.serializers import (
    CommentListSerializer,
    CommentRetrieveSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
)
from comments.services import resize_image


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.select_related('user').all()
    pagination_class = PageNumberPaginator
    serializer_classes: dict[str, Type[Serializer]] = {
        'list': CommentListSerializer,
        'retrieve': CommentRetrieveSerializer,
        'answer_list': CommentRetrieveSerializer,
        'create': CommentCreateSerializer,
        'partial_update': CommentUpdateSerializer,
    }
    permission_classes: dict[str, tuple[Type[BasePermission]]] = {
        'default': (AllowAny,),
        'create': (IsAuthenticated,),
        'partial_update': (IsOwner,),
        'destroy': (IsOwner,),
    }
    filterset_class = CommentFilter

    def get_serializer_class(self) -> Type[Serializer] | None:
        return self.serializer_classes.get(self.action)

    def get_permissions(self) -> list[BasePermission]:
        if not (permission_classes := self.permission_classes.get(self.action)):
            permission_classes = self.permission_classes['default']
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        self._resize_image(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._resize_image(request)
        return super().update(request, *args, **kwargs)

    def _resize_image(self, request):
        if image := request.data.get('image'):
            request.data['image'] = resize_image(image)
