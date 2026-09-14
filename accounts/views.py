from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User


def register(request):
    """
    Menangani proses pendaftaran user baru.
    """

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        ).strip()

        email = request.POST.get(
            'email'
        ).strip()

        password = request.POST.get(
            'password'
        )

        password_confirm = request.POST.get(
            'password_confirm'
        )


        # =========================
        # VALIDASI USERNAME
        # =========================

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username sudah digunakan.'
            )

            return redirect(
                'accounts:register'
            )


        # =========================
        # VALIDASI PASSWORD
        # =========================

        if password != password_confirm:

            messages.error(
                request,
                'Password dan konfirmasi password tidak sama.'
            )

            return redirect(
                'accounts:register'
            )


        if len(password) < 8:

            messages.error(
                request,
                'Password minimal 8 karakter.'
            )

            return redirect(
                'accounts:register'
            )


        # =========================
        # BUAT USER
        # =========================

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password

        )


        messages.success(
            request,
            'Registrasi berhasil. Silakan login.'
        )


        return redirect(
            'accounts:login'
        )


    return render(
        request,
        'accounts/register.html'
    )


def login_view(request):
    """
    Menangani proses login user.
    """

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )


        user = authenticate(

            request,

            username=username,

            password=password

        )


        if user is not None:

            login(
                request,
                user
            )

            messages.success(
                request,
                f'Selamat datang, {user.username}!'
            )

            return redirect(
                'books:home'
            )


        messages.error(
            request,
            'Username atau password salah.'
        )


    return render(
        request,
        'accounts/login.html'
    )


def logout_view(request):
    """
    Logout user.
    """

    logout(request)

    messages.success(
        request,
        'Kamu berhasil logout.'
    )

    return redirect(
        'books:home'
    )


@login_required
def profile(request):
    """
    Menampilkan profile user yang sedang login.
    """

    return render(
        request,
        'accounts/profile.html'
    )