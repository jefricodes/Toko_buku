from django.test import TestCase
from django.urls import reverse

from .models import Book, Category
from django.contrib.auth.models import User


class BookModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name='Pemrograman',
            slug='pemrograman'
        )

        self.book = Book.objects.create(
            category=self.category,
            title='Belajar Python',
            author='Budi',
            # publisher='Penerbit ABC',
            # isbn='1234567890',
            description='Buku belajar Python',
            price=100000,
            stock=10
        )

    def test_book_created(self):
        self.assertEqual(
            self.book.title,
            'Belajar Python'
        )

    def test_book_price(self):
        self.assertEqual(
            self.book.price,
            100000
        )

    def test_book_stock(self):
        self.assertEqual(
            self.book.stock,
            10
        )

class BookViewTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name='Pemrograman',
            slug='pemrograman'
        )

        self.book = Book.objects.create(
            category=self.category,
            title='Belajar Django',
            author='Andi',
            # publisher='Penerbit XYZ',
            # isbn='9876543210',
            description='Belajar Django dari dasar',
            price=150000,
            stock=5
        )

    def test_book_list_page(self):
        response = self.client.get(
            reverse('books:book_list')
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            'Belajar Django'
        )

    def test_book_detail_page(self):
        response = self.client.get(
            reverse(
                'books:book_detail',
                args=[self.book.id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            'Belajar Django'
        )


    def test_book_search(self):
        response = self.client.get(
            reverse('books:book_list'),
            {
                'search': 'Django'
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            'Belajar Django'
        )