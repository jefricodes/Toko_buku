from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User


class AccountTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )

    def test_login_page(self):
        response = self.client.get(
            reverse('accounts:login')
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_login_success(self):
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'user1',
                'password': 'password123'
            }
        )

        self.assertRedirects(
            response,
            reverse('books:home')
        )

    def test_login_failed(self):
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'user1',
                'password': 'password-salah'
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )