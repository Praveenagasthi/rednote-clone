from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

from posts.models import Post

User = get_user_model()


class SearchAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='searchuser',
            email='search@example.com',
            password='StrongPassword@2026'
        )

        self.python_user = User.objects.create_user(
            username='python_dev',
            email='python@example.com',
            password='StrongPassword@2026',
            display_name='Python Developer'
        )

        self.django_user = User.objects.create_user(
            username='django_dev',
            email='django@example.com',
            password='StrongPassword@2026',
            display_name='Django Developer'
        )

        self.python_post = Post.objects.create(
            author=self.python_user,
            caption='Learning Python programming',
            location='Bangalore'
        )

        self.django_post = Post.objects.create(
            author=self.django_user,
            caption='Learning Django REST Framework',
            location='Kochi'
        )

        self.client.force_authenticate(user=self.user)

    def test_user_search_by_username(self):
        response = self.client.get(
            '/api/search/users/?q=python'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        usernames = [
            item['username']
            for item in response.data['results']
        ]

        self.assertIn(
            'python_dev',
            usernames
        )

    def test_user_search_by_display_name(self):
        response = self.client.get(
            '/api/search/users/?q=Python Developer'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        usernames = [
            item['username']
            for item in response.data['results']
        ]

        self.assertIn(
            'python_dev',
            usernames
        )

    def test_user_search_empty_query_returns_no_results(self):
        response = self.client.get(
            '/api/search/users/?q='
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['results'],
            []
        )

    def test_post_search_by_caption(self):
        response = self.client.get(
            '/api/search/posts/?q=Python'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertIn(
            self.python_post.id,
            post_ids
        )

        self.assertNotIn(
            self.django_post.id,
            post_ids
        )

    def test_post_search_by_location(self):
        response = self.client.get(
            '/api/search/posts/?q=Kochi'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertIn(
            self.django_post.id,
            post_ids
        )

    def test_post_search_empty_query_returns_no_results(self):
        response = self.client.get(
            '/api/search/posts/?q='
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['results'],
            []
        )

    def test_user_search_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            '/api/search/users/?q=python'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_post_search_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            '/api/search/posts/?q=Python'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )