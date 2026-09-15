from django.urls import path

from . import views


app_name = 'orders'


urlpatterns = [
    path(
        'cart/',
        views.cart,
        name='cart'
    ),

    path(
        'cart/add/<int:book_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/update/<int:item_id>/',
        views.update_cart,
        name='update_cart'
    ),

    path(
        'cart/remove/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
    'success/<str:order_number>/',
    views.order_success,
    name='success'
    ),

    path(
    'orders/',
    views.order_list,
    name='order_list'
    ),

    path(
        'orders/<str:order_number>/',
        views.order_detail,
        name='order_detail'
    ),

    path(
    'my-orders/',
    views.order_list,
    name='order_list'
    ),

    path(
        'my-orders/<str:order_number>/',
        views.order_detail,
        name='order_detail'
    ),


]