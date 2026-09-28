from django.db.models import Sum

from books.models import Book
from orders.models import Order


class DashboardService:

    LOW_STOCK_LIMIT = 5

    @staticmethod
    def get_summary():

        paid_statuses = [
            'paid',
            'processing',
            'shipped',
            'completed',
        ]

        total_revenue = (Order.objects.filter(status__in=paid_statuses)
                 .aggregate(total=Sum('total'))['total'] or 0)

        return {
            'total_books': Book.objects.filter(is_active=True).count(),

            'low_stock_books': Book.objects.filter(is_active=True, stock__lte=DashboardService.LOW_STOCK_LIMIT).count(),

            'total_orders': Order.objects.count(),

            'total_revenue': total_revenue,

            'pending_orders': Order.objects.filter(status='pending').count(),

            'paid_orders': Order.objects.filter(status='paid').count(),

            'processing_orders': Order.objects.filter(status='processing').count(),

            'shipped_orders': Order.objects.filter(status='shipped').count(),

            'completed_orders': Order.objects.filter(status='completed').count(),

            'cancelled_orders': Order.objects.filter(status='cancelled').count(),
        }

    @staticmethod
    def get_recent_orders(limit=10):

        return (Order.objects.select_related('user')
                .order_by('-created_at')[:limit])

    @staticmethod
    def get_low_stock_books(limit=10):

        return (Book.objects.filter(is_active=True, stock__lte=DashboardService.LOW_STOCK_LIMIT)
            .select_related('category')
            .order_by('stock', 'title')[:limit]
        )

    
    @staticmethod
    def update_order_status(order, new_status):

        valid_statuses = {
            'pending',
            'paid',
            'processing',
            'shipped',
            'completed',
            'cancelled',
        }

        if new_status not in valid_statuses:
            raise ValueError('Status pesanan tidak valid.')
        
        current_status = order.status

        # ##################################################
        # Order yang sudah selesai tidak boleh diubah lagi
        # ##################################################

        if current_status == 'completed':
            raise ValueError('Pesanan yang sudah selesai tidak dapat diubah.')

        # ##################################################
        # Order yang dibatalkan tidak boleh diproses lagi
        # ##################################################

        if current_status == 'cancelled':
            raise ValueError('Pesanan yang sudah dibatalkan tidak dapat diubah.')

        allowed_transitions = {
            'pending': ['paid','cancelled',],
            'paid': ['processing','cancelled',],
            'processing': ['shipped',],
            'shipped': ['completed',],
        }

        if new_status not in allowed_transitions.get(
            current_status,
            []
        ):
            raise ValueError(
                f'Perubahan status dari '
                f'"{order.get_status_display()}" '
                f'ke status tersebut tidak diperbolehkan.'
            )

        order.status = new_status

        order.save(
            update_fields=['status','updated_at']
        )

        return order