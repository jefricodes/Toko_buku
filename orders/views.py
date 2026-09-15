from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from books.models import Book

from .models import Cart, Order
from .services import CartService, OrderService



@login_required
def add_to_cart(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id,
        is_active=True
    )

    if request.method == 'POST':

        try:
            quantity = int(request.POST.get('quantity',1))
        except (TypeError, ValueError):
            messages.error(request,'Jumlah buku tidak valid.')
            return redirect('books:book_detail',pk=book.id)

        try:

            CartService.add_to_cart(
                user=request.user,
                book=book,
                quantity=quantity
            )

        except ValidationError as e:

            messages.error(
                request,
                str(e)
            )

            return redirect(
                'books:book_detail',
                pk=book.id
            )

        messages.success(
            request,
            f'"{book.title}" berhasil ditambahkan '
            'ke keranjang.'
        )

        return redirect(
            'orders:cart'
        )

    return redirect(
        'books:book_detail',
        pk=book.id
    )

@login_required
def cart(request):
    cart = CartService.get_or_create_cart(
        request.user
    )

    cart_items = cart.items.select_related(
        'book'
    )

    total = cart.get_total()

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }

    return render(
        request,
        'orders/cart.html',
        context
    )


@login_required
def update_cart(request, item_id):

    if request.method == 'POST':

        try:

            quantity = int(
                request.POST.get(
                    'quantity',
                    1
                )
            )

        except (TypeError, ValueError):

            messages.error(
                request,
                'Jumlah buku tidak valid.'
            )

            return redirect(
                'orders:cart'
            )

        try:

            CartService.update_quantity(
                user=request.user,
                cart_item_id=item_id,
                quantity=quantity
            )

        except ValidationError as e:

            messages.error(
                request,
                str(e)
            )

            return redirect(
                'orders:cart'
            )

        messages.success(
            request,
            'Jumlah buku berhasil diperbarui.'
        )

    return redirect(
        'orders:cart'
    )

@login_required
def remove_from_cart(request, item_id):

    if request.method == 'POST':

        try:

            CartService.remove_from_cart(
                user=request.user,
                cart_item_id=item_id
            )

        except ValidationError as e:

            messages.error(
                request,
                str(e)
            )

            return redirect(
                'orders:cart'
            )

        messages.success(
            request,
            'Buku berhasil dihapus dari keranjang.'
        )

    return redirect(
        'orders:cart'
    )

@login_required
def checkout(request):

    cart = CartService.get_or_create_cart(
        request.user
    )

    cart_items = cart.items.select_related(
        'book'
    )

    if not cart_items.exists():

        messages.warning(
            request,
            'Keranjang kamu masih kosong.'
        )

        return redirect(
            'orders:cart'
        )

    total = cart.get_total()

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        address = request.POST.get(
            'address',
            ''
        ).strip()

        if not full_name:
            messages.error(
                request,
                'Nama lengkap wajib diisi.'
            )

            return redirect(
                'orders:checkout'
            )

        if not phone:
            messages.error(
                request,
                'Nomor telepon wajib diisi.'
            )

            return redirect(
                'orders:checkout'
            )

        if not address:
            messages.error(
                request,
                'Alamat wajib diisi.'
            )

            return redirect(
                'orders:checkout'
            )

        try:

            order = OrderService.create_order(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address=address
            )

        except ValidationError as e:

            messages.error(
                request,
                str(e)
            )

            return redirect(
                'orders:cart'
            )

        return redirect(
            'orders:success',
            order_number=order.order_number
        )

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }

    return render(
        request,
        'orders/checkout.html',
        context
    )


@login_required
def order_success(request, order_number):

    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )

    context = {
        'order': order
    }

    return render(
        request,
        'orders/success.html',
        context
    )

@login_required
def order_list(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'orders': orders
    }

    return render(
        request,
        'orders/order_list.html',
        context
    )

@login_required
def order_detail(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items'
        ),
        order_number=order_number,
        user=request.user
    )

    context = {
        'order': order
    }

    return render(
        request,
        'orders/order_detail.html',
        context
    )