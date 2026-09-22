from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class UserRegistrationTests(APITestCase):

    def test_user_registration(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword@2026'
        }

        response = self.client.post(
            '/api/auth/register/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            User.objects.filter(username='testuser').exists()
        )

    def test_weak_password_rejected(self):
        data = {
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password': 'password'
        }

        response = self.client.post(
            '/api/auth/register/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            User.objects.filter(username='weakuser').exists()
        )

class AuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='StrongPassword@2026'
        )

    def test_login_returns_tokens(self):
        data = {
            'username': 'authuser',
            'password': 'StrongPassword@2026'
        }

        response = self.client.post(
            '/api/auth/login/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login_rejected(self):
        data = {
            'username': 'authuser',
            'password': 'WrongPassword123!'
        }

        response = self.client.post(
            '/api/auth/login/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

class ProtectedEndpointTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='protecteduser',
            email='protected@example.com',
            password='StrongPassword@2026'
        )

    def test_notifications_require_authentication(self):
        response = self.client.get(
            '/api/auth/notifications/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unread_count_requires_authentication(self):
        response = self.client.get(
            '/api/auth/notifications/unread-count/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_authenticated_user_can_access_notifications(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            '/api/auth/notifications/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )