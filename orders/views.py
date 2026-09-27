from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from books.models import Book

from .models import Cart, Order, CartItem, OrderItem
from .services import (CartService, OrderService)

from .payment import MidtransService

import hashlib
import hmac

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



@login_required
def add_to_cart(request, book_id):

    book = get_object_or_404(Book,id=book_id,is_active=True)

    if request.method == 'POST':

        try:
            quantity = int(request.POST.get('quantity',1))
        except (TypeError, ValueError):
            messages.error(request,'Jumlah buku tidak valid.')
            return redirect('books:book_detail',pk=book.id)

        try:

            CartService.add_to_cart(user=request.user,book=book,quantity=quantity)

        except ValidationError as e:
            messages.error(request,str(e))
            return redirect('books:book_detail',pk=book.id)

        messages.success(request,f'"{book.title}" berhasil ditambahkan ''ke keranjang.')
        return redirect('orders:cart')

    return redirect('books:book_detail',pk=book.id)

@login_required
def cart(request):
    cart = CartService.get_or_create_cart(request.user)
    cart_items = cart.items.select_related('book')
    total = cart.get_total()
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }

    return render(request,'orders/cart.html',context)


@login_required
def update_cart(request, item_id):

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity',1))

        except (TypeError, ValueError):
            messages.error(request,'Jumlah buku tidak valid.')
            return redirect('orders:cart')

        try:

            CartService.update_quantity(
                user=request.user,
                cart_item_id=item_id,
                quantity=quantity
            )

        except ValidationError as e:
            messages.error(request,str(e))
            return redirect('orders:cart')

        messages.success(request,'Jumlah buku berhasil diperbarui.')

    return redirect('orders:cart')

@login_required
def remove_from_cart(request, item_id):

    if request.method == 'POST':

        try:
            CartService.remove_from_cart(
                user=request.user,
                cart_item_id=item_id
            )

        except ValidationError as e:
            messages.error(request,str(e))
            return redirect('orders:cart')
        
        messages.success(request,'Buku berhasil dihapus dari keranjang.')

    return redirect('orders:cart')

@login_required
def checkout(request):

    cart = CartService.get_or_create_cart(request.user)
    cart_items = cart.items.select_related('book')
    if not cart_items.exists():
        messages.warning(request,'Keranjang kamu masih kosong.')
        return redirect('orders:cart')
    
    total = cart.get_total()
    if request.method == 'POST':
        full_name = request.POST.get('full_name','').strip()
        phone = request.POST.get('phone','').strip()
        address = request.POST.get('address','').strip()

        if not full_name:
            messages.error(request,'Nama lengkap wajib diisi.')
            return redirect('orders:checkout')

        if not phone:
            messages.error(request,'Nomor telepon wajib diisi.')
            return redirect('orders:checkout')

        if not address:
            messages.error(request,'Alamat wajib diisi.')
            return redirect('orders:checkout')

        try:

            order = OrderService.create_order(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address=address
            )

        except ValidationError as e:
            messages.error(request,str(e))
            return redirect('orders:cart')

        return redirect('orders:success',order_number=order.order_number)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }

    return render(request,'orders/checkout.html',context)


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {
        'order': order
    }
    return render(request,'orders/success.html',context)

@login_required
def order_list(request):

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request,'orders/order_list.html',context)

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'),
        order_number=order_number,
        user=request.user
    )

    context = {
        'order': order
    }
    return render(request,'orders/order_detail.html',context)
# #####################
# Midtrans Service
# #####################

@login_required
def create_payment(request, order_number):
    order = get_object_or_404(Order,order_number=order_number,user=request.user)
    if order.status != 'pending':
        messages.warning(request,'Order ini tidak membutuhkan pembayaran.')

        return redirect('orders:order_detail',order_number=order.order_number)

    try:
        transaction = (MidtransService.create_transaction(order))
        order.midtrans_order_id = (order.order_number)
        order.payment_token = (transaction.get('token'))
        order.payment_url = (transaction.get('redirect_url'))
        order.save(
            update_fields=[
                'midtrans_order_id',
                'payment_token',
                'payment_url',
                'updated_at'
            ]
        )

        return redirect(order.payment_url)

    except Exception:
        messages.error(request,'Gagal membuat transaksi pembayaran.')

        return redirect('orders:order_detail',order_number=order.order_number)

import json
import logging
logger = logging.getLogger(__name__)
@csrf_exempt
@require_POST
def midtrans_notification(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError :
        return JsonResponse ({'detail': 'Invalid JSON Payload'}, status=400)
    
    order_id = data.get('order_id')
    status_code = data.get('status_code')
    gross_amount = data.get('gross_amount')
    signature_key = data.get('signature_key')


    # data = request.data if hasattr(request, 'data') else request.POST
    # order_id = data.get('order_id')
    # status_code = data.get('status_code')
    # gross_amount = data.get('gross_amount')
    # signature_key = data.get('signature_key')

    if not all([
        order_id,
        status_code,
        gross_amount,
        signature_key
    ]):
        return JsonResponse(
            {
                'detail': 'Data notification tidak lengkap.'
            },
            status=400
        )

    raw_signature = (
        f'{order_id}'
        f'{status_code}'
        f'{gross_amount}'
        f'{settings.MIDTRANS_SERVER_KEY}'
    )

    calculated_signature = hashlib.sha512(raw_signature.encode('utf-8')).hexdigest()
    if not hmac.compare_digest(calculated_signature, signature_key):

        return JsonResponse({ 'detail': 'Signature tidak valid.'}, status=403)

    try:
        order = Order.objects.get( order_number=order_id )

    except Order.DoesNotExist:
        return JsonResponse({ 'detail': 'Order tidak ditemukan.'}, status=404)

    if str(order.total) != str(gross_amount):

        return JsonResponse({ 'detail': 'Nominal pembayaran tidak sesuai.'}, status=400)
    
    transaction_status = data.get('transaction_status')

    fraud_status = data.get('fraud_status')

    if transaction_status in [
        'settlement',
        'capture'
    ]:

        if (transaction_status == 'capture' and fraud_status and fraud_status != 'accept'):
            return JsonResponse({'detail':'Transaksi capture belum diterima.'},status=200)

        try:
            OrderService.complete_payment(order)

        except ValidationError as e:
            return JsonResponse({'detail': str(e)}, status=400)

    elif transaction_status == 'pending':
        order.status = 'pending'
        order.save(update_fields=['status','updated_at'])

    elif transaction_status in ['cancel','deny','expire']:

        order.status = 'cancelled'
        order.save(update_fields=['status','updated_at'])
    else:
        logger.warning (f'Unhandled transaction status : {transaction_status} for order {order_id}')

    return JsonResponse ({'detail': 'Notification berhasil diproses.'},status=200)