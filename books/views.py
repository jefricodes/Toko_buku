from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Book, Category


def home(request):
    """
    Menampilkan 8 buku terbaru di halaman utama.
    """

    books = Book.objects.filter(
        is_active=True
    )[:8]

    context = {
        'books': books
    }

    return render(
        request,
        'home.html',
        context
    )


def book_list(request):
    """
    Menampilkan daftar buku.

    Fitur:
    - Search berdasarkan judul, penulis, ISBN
    - Filter berdasarkan kategori
    - Pagination
    """

    books = Book.objects.filter(is_active=True).select_related('category')

    # =========================
    # SEARCH
    # =========================

    search = request.GET.get('q','') or request.GET.get('seerch', '')
    search = search.strip()

    if search:

        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) 
        )
            # Q(isbn__icontains=search)
        

    # =========================
    # FILTER KATEGORI
    # =========================

    category_slug = request.GET.get('category','').strip()

    if category_slug:
        books = books.filter(
            category__slug=category_slug
        )

    # =========================
    # PAGINATION
    # =========================

    paginator = Paginator(
        books,
        8
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    categories = Category.objects.all()

    context = {
        'books': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'selected_category': category_slug,
    }

    return render(
        request,
        'books/list.html',
        context
    )


def book_detail(request, pk):
    """
    Menampilkan detail sebuah buku.
    """

    book = get_object_or_404(
        Book,
        pk=pk,
        is_active=True
    )

    context = {
        'book': book
    }

    return render(
        request,
        'books/detail.html',
        context
    )


def book_create(request):
    """
    Menambahkan buku baru.
    """

    categories = Category.objects.all()

    if request.method == 'POST':

        title = request.POST.get('title')
        author = request.POST.get('author')
        # publisher = request.POST.get('publisher')
        # isbn = request.POST.get('isbn')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        cover = request.FILES.get('cover')

        # Validasi sederhana

        if not title:
            messages.error(
                request,
                'Judul buku wajib diisi.'
            )

            return redirect(
                'books:book_create'
            )

        if not category_id:
            messages.error(
                request,
                'Kategori wajib dipilih.'
            )

            return redirect(
                'books:book_create'
            )

        # Membuat buku

        Book.objects.create(
            title=title,
            author=author,
            # publisher=publisher,
            # isbn=isbn,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            cover=cover
        )

        messages.success(
            request,
            'Buku berhasil ditambahkan.'
        )

        return redirect(
            'books:book_list'
        )

    context = {
        'categories': categories
    }

    return render(
        request,
        'books/form.html',
        context
    )


def book_update(request, pk):
    """
    Mengedit buku.
    """

    book = get_object_or_404(
        Book,
        pk=pk
    )

    categories = Category.objects.all()

    if request.method == 'POST':

        book.title = request.POST.get(
            'title'
        )

        book.author = request.POST.get(
            'author'
        )

        # book.publisher = request.POST.get(
        #     'publisher'
        # )

        # book.isbn = request.POST.get(
        #     'isbn'
        # )

        book.description = request.POST.get(
            'description'
        )

        book.price = request.POST.get(
            'price'
        )

        book.stock = request.POST.get(
            'stock'
        )

        book.category_id = request.POST.get(
            'category'
        )

        cover = request.FILES.get(
            'cover'
        )

        if cover:
            book.cover = cover

        book.save()

        messages.success(
            request,
            'Buku berhasil diperbarui.'
        )

        return redirect(
            'books:book_list'
        )

    context = {
        'book': book,
        'categories': categories
    }

    return render(
        request,
        'books/form.html',
        context
    )


def book_delete(request, pk):
    """
    Menghapus buku.
    """

    book = get_object_or_404(
        Book,
        pk=pk
    )

    if request.method == 'POST':

        book.delete()

        messages.success(
            request,
            'Buku berhasil dihapus.'
        )

        return redirect(
            'books:book_list'
        )

    context = {
        'book': book
    }

    return render(
        request,
        'books/delete.html',
        context
    )