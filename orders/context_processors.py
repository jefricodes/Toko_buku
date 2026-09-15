from .models import Cart


def cart_count(request):

    count = 0

    if request.user.is_authenticated:

        try:

            cart = request.user.cart

            count = sum(
                item.quantity
                for item in cart.items.all()
            )

        except Cart.DoesNotExist:

            count = 0

    return {
        'cart_count': count
    }