from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import (render, redirect, get_object_or_404)

from .services import DashboardService
from orders.models import Order

from django.views.decorators.http import require_POST
from django.contrib import messages




@login_required
def dashboard_home(request):
    if not request.user.is_staff:
        raise PermissionDenied

    summary = DashboardService.get_summary()

    recent_orders = (DashboardService.get_recent_orders())

    low_stock_books = (DashboardService.get_low_stock_books())

    context = {
        'summary': summary,
        'recent_orders': recent_orders,
        'low_stock_books': low_stock_books,
    }

    return render(request,'dashboard/index.html',context)

@login_required
def order_list(request):

    if not request.user.is_staff:
        raise PermissionDenied

    orders = (
        Order.objects
        .select_related('user')
        .order_by('-created_at')
    )

    context = {
        'orders': orders,
    }

    return render(request, 'dashboard/order_list.html', context)

@login_required
def order_detail(request, order_number):

    if not request.user.is_staff:
        raise PermissionDenied

    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)

    context = {
        'order': order,
    }

    return render(request, 'dashboard/order_detail.html', context)

@login_required
@require_POST
def update_order_status(request, order_number):

    if not request.user.is_staff:
        raise PermissionDenied

    order = get_object_or_404(Order, order_number=order_number)

    new_status = request.POST.get('status')

    try:
        DashboardService.update_order_status(order, new_status)

        messages.success(request,'Status pesanan berhasil diperbarui.')

    except ValueError as e:
        messages.error(request,str(e))

    return redirect('dashboard:order_detail', order_number=order.order_number)
