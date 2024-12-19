import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from comments.models import Comment
from comments.serializers import (
    CommentListSerializer,
    CommentRetrieveSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
)
from tests.comments.conftest import get_uploaded_file, get_uploaded_image


@pytest.mark.django_db(transaction=True)
class TestListView:
    url = reverse('comment-list')
    serializer_class = CommentListSerializer

    @pytest.fixture(autouse=True)
    def comments(self, comment_factory, owner):
        comment_factory.create_batch(60, user=owner)

    def test_view_paginates_comments_into_25_pieces_per_page(self, api_client):
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 25
        assert response.data['count'] == 60
        assert response.data['total_pages'] == 3
        assert response.data['current_page'] == 1
        assert '?page=1' in str(response.data['first'])
        assert '?page=3' in str(response.data['last'])
        assert '?page=2' in str(response.data['next'])
        assert response.data['previous'] is None

    def test_view_returns_expected_data(self, api_client):
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

        comment_data = response.data['results'][0]
        expected_comment = Comment.objects.get(uuid=comment_data['uuid'])
        expected_data = self.serializer_class(instance=expected_comment).data
        assert comment_data == expected_data

    def test_view_returns_filtered_data_by_target(self, comment_factory, api_client):
        first_comment = Comment.objects.first()
        last_comment = Comment.objects.last()
        comment_factory.create(target=first_comment)
        comment_factory.create(target=last_comment)

        response = api_client.get(self.url, data={'target_is_null': True})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 25
        assert response.data['count'] == 60

        response = api_client.get(self.url, data={'target_is_null': False})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert response.data['count'] == 2

        response = api_client.get(self.url, data={'target': first_comment.uuid})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['count'] == 1


@pytest.mark.django_db(transaction=True)
class TestRetrieveView:
    serializer_class = CommentRetrieveSerializer

    @pytest.fixture()
    def url(self, comment):
        return reverse('comment-detail', [comment.uuid])

    def test_view_returns_expected_data(self, api_client, url, comment):
        response = api_client.get(url)

        expected_data = self.serializer_class(instance=comment).data

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data


@pytest.mark.django_db(transaction=True)
class TestCreateView:
    serializer_class = CommentCreateSerializer
    url = reverse('comment-list')

    @pytest.fixture()
    def test_data(self, owner, test_image, test_file):
        return {
            'user': str(owner.id),
            'text': 'Some text',
            'file': test_file,
            'image': test_image,
        }

    def test_view_isnt_allowed_for_unauthenticated_user(self, test_media_root, api_client, test_data):
        assert Comment.objects.count() == 0

        response = api_client.post(self.url, data=test_data, format='multipart')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.count() == 0

    def test_view_create_comment(self, test_media_root, owner, api_client, test_data):
        api_client.force_login(owner)
        assert Comment.objects.count() == 0

        response = api_client.post(self.url, data=test_data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == 1

        comment = Comment.objects.first()

        assert comment.user.id == int(test_data['user'])
        assert comment.text == test_data['text']
        test_data['file'].seek(0)
        assert comment.file.read() == test_data['file'].read()
        test_data['image'].seek(0)
        assert comment.image.read() == test_data['image'].read()

    def test_view_returns_expected_data(self, test_media_root, api_client, test_data, owner, test_request):
        api_client.force_login(owner)

        response = api_client.post(self.url, data=test_data, format='multipart')

        comment = Comment.objects.first()
        expected_data = self.serializer_class(instance=comment, context={'request': test_request}).data

        assert response.data == expected_data


@pytest.mark.django_db(transaction=True)
class TestPatchUpdateView:
    serializer_class = CommentUpdateSerializer

    @pytest.fixture()
    def test_comment(self, owner, comment_factory):
        return comment_factory.create(user=owner, text='Text')

    @pytest.fixture()
    def url(self, test_comment):
        return reverse('comment-detail', [test_comment.uuid])

    @pytest.fixture()
    def test_data(self):
        return {
            'text': 'new text',
            'image': get_uploaded_image(extra_size=100),
            'file': get_uploaded_file(size=100),
        }

    def test_view_doesnt_allow_to_update_comment_if_user_isnt_owner_for_it(
        self, test_comment, test_media_root, not_owner, api_client, test_data
    ):
        url_ = reverse('comment-detail', [test_comment.uuid])
        api_client.force_login(not_owner)

        assert test_comment.text != test_data['text']
        assert test_comment.file.name is None
        assert test_comment.image.name is None

        response = api_client.patch(url_, data=test_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        test_comment.refresh_from_db()
        assert test_comment.text != test_data['text']
        assert test_comment.file.name == ''
        assert test_comment.image.name == ''

    def test_view_updates_comment(self, url, test_comment, test_media_root, owner, api_client, test_data, test_request):
        api_client.force_login(owner)

        assert test_comment.text != test_data['text']
        assert test_comment.file.name is None
        assert test_comment.image.name is None

        response = api_client.patch(url, data=test_data)

        assert response.status_code == status.HTTP_200_OK
        test_comment.refresh_from_db()
        assert test_comment.text == test_data['text']
        test_data['image'].seek(0)
        assert test_comment.image.read() == test_data['image'].read()
        test_data['file'].seek(0)
        assert test_comment.file.read() == test_data['file'].read()

    def test_view_returns_expected_data(
        self, url, test_comment, test_media_root, owner, api_client, test_data, test_request
    ):
        api_client.force_login(owner)

        response = api_client.patch(url, data=test_data)

        assert response.status_code == status.HTTP_200_OK

        test_comment.refresh_from_db()
        expected_data = self.serializer_class(instance=test_comment, context={'request': test_request}).data
        assert response.data == expected_data


@pytest.mark.django_db(transaction=True)
class TestDeleteView:
    @pytest.fixture()
    def test_comment(self, owner, comment_factory):
        return comment_factory.create(user=owner, text='Text')

    @pytest.fixture()
    def url(self, test_comment):
        return reverse('comment-detail', [test_comment.uuid])

    def test_view_deletes_comment(self, url, test_comment, owner, api_client):
        api_client.force_login(owner)

        assert Comment.objects.count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Comment.objects.count() == 0

    def test_view_doesnt_allow_to_delete_comment_if_user_isnt_owner_for_it(
        self, not_owner, url, test_comment, api_client
    ):
        api_client.force_login(not_owner)

        assert Comment.objects.count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.count() == 1
