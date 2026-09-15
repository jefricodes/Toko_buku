from django.urls import path

from . import views


app_name = 'api'


urlpatterns = [

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

]