import base64

from django.contrib.auth.models import (
    Permission,
    User,
)
from django.test import TestCase
from rest_framework import (
    HTTP_HEADER_ENCODING,
    status,
)
from rest_framework.test import APIRequestFactory
from testapp.models import (
    Author,
    Book,
)
from testapp.views import (
    book_list_view,
    book_view,
    special_book_view,
)


factory = APIRequestFactory()


def basic_auth_header(username, password):
    credentials = ('%s:%s' % (username, password))
    base64_credentials = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode(HTTP_HEADER_ENCODING)
    return 'Basic %s' % base64_credentials


class ModelActionPermissionsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user('disallowed', 'disallowed@example.com', 'password')
        user = User.objects.create_user('permitted', 'permitted@example.com', 'password')
        user.user_permissions.set([
            Permission.objects.get(codename='add_book'),
            Permission.objects.get(codename='change_book'),
            Permission.objects.get(codename='delete_book')
        ])

        cls.permitted_credentials = basic_auth_header('permitted', 'password')
        cls.disallowed_credentials = basic_auth_header('disallowed', 'password')

        cls.book = Book.objects.create(
            author=Author.objects.create(first_name='John', last_name='Smith'),
            title='Some book',
        )

    def test_has_create_permissions(self):
        request = factory.post(
            '/',
            {'title': 'New book', 'author': self.book.author_id},
            format='json',
            HTTP_AUTHORIZATION=self.permitted_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_has_update_permissions(self):
        request = factory.put(
            '/',
            {'title': 'Changed book', 'author': self.book.author_id},
            format='json',
            HTTP_AUTHORIZATION=self.permitted_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_has_partial_update_permissions(self):
        request = factory.patch(
            '/',
            {'title': 'Changed book'},
            format='json',
            HTTP_AUTHORIZATION=self.permitted_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_has_destroy_permissions(self):
        request = factory.delete(
            '/',
            {},
            format='json',
            HTTP_AUTHORIZATION=self.permitted_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_has_retrieve_permissions(self):
        request = factory.get(
            '/',
            {},
            format='json',
            HTTP_AUTHORIZATION=self.permitted_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_has_list_permissions(self):
        request = factory.get(
            '/',
            {},
            format='json',
            HTTP_AUTHORIZATION=self.permitted_credentials,
        )
        response = book_list_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_has_not_create_permissions(self):
        request = factory.post(
            '/',
            {'title': 'New book', 'author': self.book.author_id},
            format='json',
            HTTP_AUTHORIZATION=self.disallowed_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_has_not_update_permissions(self):
        request = factory.put(
            '/',
            {'title': 'Changed book', 'author': self.book.author_id},
            format='json',
            HTTP_AUTHORIZATION=self.disallowed_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_has_not_partial_update_permissions(self):
        request = factory.patch(
            '/',
            {'title': 'Changed book'},
            format='json',
            HTTP_AUTHORIZATION=self.disallowed_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_has_not_destroy_permissions(self):
        request = factory.delete(
            '/',
            {},
            format='json',
            HTTP_AUTHORIZATION=self.disallowed_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_has_not_retrieve_permissions(self):
        request = factory.get(
            '/',
            {},
            format='json',
            HTTP_AUTHORIZATION=self.disallowed_credentials,
        )
        response = book_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ObjectActionPermissionsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user('permitted', 'permitted@example.com', 'password')
        cls.credentials = basic_auth_header('permitted', 'password')

        cls.permitted_book = Book.objects.create(
            author=Author.objects.create(first_name='John', last_name='Smith'),
            title='Special book',
        )
        cls.not_permitted_book = Book.objects.create(
            author=Author.objects.create(first_name='Kate', last_name='Smith'),
            title='Some book',
        )
        cls.author_not_permitted_book = Book.objects.create(
            author=Author.objects.create(first_name='Kate', last_name='Smith'),
            title='Special other book',
        )

    def test_has_retrieve_permission(self):
        request = factory.get(
            '/',
            {},
            format='json',
            HTTP_AUTHORIZATION=self.credentials,
        )
        response = special_book_view(request, pk=self.permitted_book.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_has_not_retrieve_permission(self):
        request = factory.get(
            '/',
            {},
            format='json',
            HTTP_AUTHORIZATION=self.credentials,
        )
        response = special_book_view(request, pk=self.not_permitted_book.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_has_update_permission(self):
        request = factory.put(
            '/',
            {'title': 'Special new title', 'author': self.permitted_book.author_id},
            format='json',
            HTTP_AUTHORIZATION=self.credentials,
        )
        response = special_book_view(request, pk=self.permitted_book.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_has_not_update_permission(self):
        request = factory.put(
            '/',
            {},
            format='json',
            HTTP_AUTHORIZATION=self.credentials,
        )
        response = special_book_view(request, pk=self.author_not_permitted_book.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
