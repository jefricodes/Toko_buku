from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book, Category

class BookApiTest (TestCase):
    def setUp(self):
        self.client = APIClient()
        self.normal_user = User.objects.create_user(username='user1', password='pass123')
        self.admin = User.objects.create_user(username='admin', password='pass123', is_staff = True)

        self.kat_fiksi = Category.objects.create(name='Fiksi', slug = 'fiksi')
        self.kat_sejarah = Category.objects.create(name='Sejarah', slug='sejarah')
        self.buku1 = Book.objects.create(title = 'Laut Bercerita', category=self.kat_fiksi, price=100000, stock=10, is_active=True)
        self.buku2 = Book.objects.create(title='Pulang', category=self.kat_fiksi, price=90000, stock=5, is_active=True)
        self.buku3 = Book.objects.create (title='Sejarah Dunia', category=self.kat_sejarah, price= 150000, stock=15, is_active=True)

    def test_search_books_by_category(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse ('api:book-list')
        response = self.client.get(url, {'category':'Fiksi'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        titles =[book['title'] for book in response.data]
        self.assertNotIn('Sejarah Dunia', titles)

    def test_regular_user_cannot_create_book(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('api:book-list')
        response = self.client.post(url, {
            'title': 'Buku Ilegal',
            'author':'Test Author',
            'category':self.kat_fiksi.id,
            'price': 50000,
            'stock':10,
            'description': 'test'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_book(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse ('api:book-list')
        response = self.client.post(url, {
            'title': 'Buku Admin',
            'author':'Test Author',
            'category': self.kat_fiksi.id,
            'price':75000,
            'stock':5,
            'description': 'Test'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)