from django.urls import path

from . import views


app_name = 'books'


urlpatterns = [

    # =========================
    # PUBLIC
    # =========================

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'books/',
        views.book_list,
        name='book_list'
    ),

    path(
        'books/<int:pk>/',
        views.book_detail,
        name='book_detail'
    ),

    # =========================
    # CRUD
    # =========================

    path(
        'books/tambah/',
        views.book_create,
        name='book_create'
    ),

    path(
        'books/<int:pk>/edit/',
        views.book_update,
        name='book_update'
    ),

    path(
        'books/<int:pk>/hapus/',
        views.book_delete,
        name='book_delete'
    ),
]