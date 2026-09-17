from django.urls import path

from . import views


app_name = 'dashboard'


urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_number>/status/', views.update_order_status, name='update_order_status'),
]