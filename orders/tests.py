from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from books.models import Book, Category
from .models import Cart, CartItem
from .services import CartService

from .services import OrderService
from .models import Order, OrderItem


class CartServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user1',
            password='password123'
        )

        self.category = Category.objects.create(
            name='Pemrograman',
            slug='pemrograman'
        )

        self.book = Book.objects.create(
            category=self.category,
            title='Belajar Python',
            author='Budi',
            # publisher='ABC',
            # isbn='1111111111',
            description='Belajar Python',
            price=100000,
            stock=10
        )

    def test_create_cart(self):
        cart = CartService.get_or_create_cart(
            self.user
        )

        self.assertEqual(
            cart.user,
            self.user
        )

    def test_add_book_to_cart(self):
        cart = CartService.add_to_cart(
            user=self.user,
            book=self.book,
            quantity=2
        )

        item = CartItem.objects.get(
            cart=cart,
            book=self.book
        )

        self.assertEqual(
            item.quantity,
            2
        )

    def test_add_same_book_increases_quantity(self):
        CartService.add_to_cart(
            user=self.user,
            book=self.book,
            quantity=2
        )

        CartService.add_to_cart(
            user=self.user,
            book=self.book,
            quantity=3
        )

        cart = Cart.objects.get(
            user=self.user
        )

        item = CartItem.objects.get(
            cart=cart,
            book=self.book
        )

        self.assertEqual(
            item.quantity,
            5
        )

    def test_cannot_add_more_than_stock(self):
        with self.assertRaises(ValidationError):

            CartService.add_to_cart(
                user=self.user,
                book=self.book,
                quantity=20
            )

class OrderServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer',
            password='password123'
        )

        self.category = Category.objects.create(
            name='Pemrograman',
            slug='pemrograman'
        )

        self.book = Book.objects.create(
            category=self.category,
            title='Django Dasar',
            author='Andi',
            # publisher='ABC',
            # isbn='2222222222',
            description='Belajar Django',
            price=100000,
            stock=10
        )

        CartService.add_to_cart(
            user=self.user,
            book=self.book,
            quantity=2
        )

    def test_create_order(self):
        order = OrderService.create_order(
            user=self.user,
            full_name='User Test',
            phone='08123456789',
            address='Jl. Test No. 1'
        )

        self.assertIsNotNone(
            order
        )

        self.assertEqual(
            order.user,
            self.user
        )

        self.assertEqual(
            order.total,
            200000
        )

    def test_stock_not_decreases_when_order_created(self):

        OrderService.create_order(
            user=self.user,
            full_name='User Test',
            phone='08123456789',
            address='Jl. Test No. 1'
        )

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.stock,
            10
        )

    def test_stock_decreases_after_payment(self):

        order = OrderService.create_order(
            user=self.user,
            full_name='User Test',
            phone='08123456789',
            address='Jl. Test No. 1'
        )

        OrderService.complete_payment(
            order
        )

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.stock,
            8
        )

    def test_order_becomes_paid(self):

        order = OrderService.create_order(
            user=self.user,
            full_name='User Test',
            phone='08123456789',
            address='Jl. Test No. 1'
        )

        OrderService.complete_payment(
            order
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            'paid'
        )

    def test_payment_is_idempotent(self):

        order = OrderService.create_order(
            user=self.user,
            full_name='User Test',
            phone='08123456789',
            address='Jl. Test No. 1'
        )

        OrderService.complete_payment(
            order
        )

        OrderService.complete_payment(
            order
        )

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.stock,
            8
        )

    def test_cart_cleared_after_payment(self):

        order = OrderService.create_order(
            user=self.user,
            full_name='User Test',
            phone='08123456789',
            address='Jl. Test No. 1'
        )

        OrderService.complete_payment(
            order
        )

        cart = Cart.objects.get(
            user=self.user
        )

        self.assertEqual(
            cart.items.count(),
            0
        )


