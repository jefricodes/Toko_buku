from django.urls import path

from . import views

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



app_name = 'api'


urlpatterns = [

    # =========================
    # JWT
    # =========================
    path ('token/',TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path ('token/refresh/', TokenRefreshView.as_view, name='token_refresh'),

    # =========================
    # BOOKS
    # =========================

    path(
        'books/',
        views.BookListCreateAPIView.as_view(),
        name='book-list'
    ),

    path(
        'books/<int:pk>/',
        views.BookDetailAPIView.as_view(),
        name='book-detail'
    ),


    # =========================
    # CART
    # =========================

    path(
        'cart/',
        views.CartAPIView.as_view(),
        name='cart'
    ),

    path(
        'cart/add/',
        views.CartAddAPIView.as_view(),
        name='cart-add'
    ),

    path(
        'cart/items/<int:item_id>/',
        views.CartItemUpdateAPIView.as_view(),
        name='cart-item-update'
    ),

    path(
        'cart/items/<int:item_id>/delete/',
        views.CartItemDeleteAPIView.as_view(),
        name='cart-item-delete'
    ),


    # =========================
    # ORDERS
    # =========================

    path(
        'orders/',
        views.OrderListAPIView.as_view(),
        name='order-list'
    ),

    path(
        'orders/create/',
        views.OrderCreateAPIView.as_view(),
        name='order-create'
    ),

    path(
        'orders/<str:order_number>/',
        views.OrderDetailAPIView.as_view(),
        name='order-detail'
    ),


]

