import uuid
from django.db import transaction
from django.core.exceptions import ValidationError

from books.models import Book

from .models import Cart, CartItem, Order, OrderItem


class CartService:
    @staticmethod
    def get_or_create_cart(user):
        cart, created = Cart.objects.get_or_create( user=user )
        return cart

    @staticmethod
    def add_to_cart(user, book, quantity=1):

        # Validasi quantity
        if quantity < 1:
            raise ValidationError( 'Jumlah buku minimal 1.')

        # Validasi stok
        if book.stock < 1:
            raise ValidationError('Buku sedang habis.')

        cart = CartService.get_or_create_cart (user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

        # Jika item sudah ada
        if not created:

            new_quantity = (cart_item.quantity + quantity)

            if new_quantity > book.stock:
                raise ValidationError(f'Jumlah melebihi stok. 'f'Stok tersedia: {book.stock}')

            cart_item.quantity = new_quantity

        else:

            if quantity > book.stock:
                raise ValidationError(f'Jumlah melebihi stok. 'f'Stok tersedia: {book.stock}.')
            
            cart_item.quantity = quantity

        cart_item.save()
        return cart

    @staticmethod
    def update_quantity(user, cart_item_id, quantity):

        if quantity < 1:
            raise ValidationError('Jumlah buku minimal 1.')

        cart = CartService.get_or_create_cart(user)

        try:
            cart_item = CartItem.objects.select_related('book').get(id=cart_item_id, cart=cart)

        except CartItem.DoesNotExist:
            raise ValidationError('Item tidak ditemukan.')

        if quantity > cart_item.book.stock:
            raise ValidationError(f'Jumlah melebihi stok. 'f'Stok tersedia: {cart_item.book.stock}.')

        cart_item.quantity = quantity

        cart_item.save()

        return cart

    @staticmethod
    def remove_from_cart(user, cart_item_id):

        cart = CartService.get_or_create_cart(user)

        try:
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                cart=cart
            )

        except CartItem.DoesNotExist:
            raise ValidationError('Item tidak ditemukan.')

        cart_item.delete()

        return cart

class OrderService:

    @staticmethod
    def generate_order_number():
        return (
            f"ORD-"
            f"{uuid.uuid4().hex[:12].upper()}"
        )


    @staticmethod
    @transaction.atomic

    def create_order(
        user,
        full_name,
        phone,
        address
    ):

        cart = Cart.objects.select_for_update().get(user=user)

        cart_items = list(cart.items.select_related('book'))

        if not cart_items:
            raise ValidationError('Keranjang masih kosong.')

        book_ids = [
            item.book_id
            for item in cart_items
        ]

        books = (Book.objects.select_for_update().filter(id__in=book_ids))

        books_by_id = {book.id: book for book in books}

        total = 0

        for item in cart_items:

            book = books_by_id.get(item.book_id)

            if book is None:
                raise ValidationError('Buku tidak ditemukan.')

            if book.stock < item.quantity:
                raise ValidationError(f'Stok buku "{book.title}" 'f'tidak mencukupi.')

            total += (book.price * item.quantity)

        order = Order.objects.create(
            user=user,
            order_number=OrderService.generate_order_number(),
            full_name=full_name,
            phone=phone,
            address=address,
            total=total,
            status='pending'
        )

        for item in cart_items:

            book = books_by_id[item.book_id]

            subtotal = (book.price * item.quantity)

            OrderItem.objects.create(
                order=order,
                book=book,
                book_title=book.title,
                price=book.price,
                quantity=item.quantity,
                subtotal=subtotal
            )

        return order

    @staticmethod
    @transaction.atomic
    def complete_payment(order):

        order = (Order.objects.select_for_update().get(id=order.id))

        if order.status == 'paid':
            return order

        if order.status != 'pending':
            raise ValidationError('Order tidak dapat dibayar.')

        order_items = (order.items.select_related('book'))

        for item in order_items:

            if item.book is None:
                raise ValidationError(f'Buku "{item.book_title}" 'f'tidak tersedia.')

            book = (Book.objects.select_for_update().get(id=item.book_id))

            if book.stock < item.quantity:
                raise ValidationError(f'Stok buku "{book.title}" 'f'tidak mencukupi.')

            book.stock -= item.quantity

            book.save(update_fields=['stock'])

        order.status = 'paid'

        order.save(update_fields=['status','updated_at'])

        cart = Cart.objects.get(user=order.user)

        cart.items.all().delete()

        return order

 