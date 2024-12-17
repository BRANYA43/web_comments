from unittest.mock import MagicMock

import pytest
from rest_framework.permissions import IsAuthenticated

from comments.permissions import IsOwner


class TestIsOwnerPermission:
    permission = IsOwner()

    @pytest.fixture()
    def test_request(self):
        return MagicMock(user='owner')

    @pytest.fixture()
    def test_owner_object(self):
        return MagicMock(user='owner')

    @pytest.fixture()
    def test_not_owner_object(self):
        return MagicMock(user='not_owner')

    def test_permission_inherits_is_authenticated(self):
        assert issubclass(IsOwner, IsAuthenticated)

    def test_permission_returns_true_if_user_is_owns_object(self, test_request, test_owner_object):
        result = self.permission.has_object_permission(test_request, None, test_owner_object)
        assert result is True

    def test_permission_returns_false_if_user_doesnt_own_for_object(self, test_request, test_not_owner_object):
        result = self.permission.has_object_permission(test_request, None, test_not_owner_object)
        assert result is False
