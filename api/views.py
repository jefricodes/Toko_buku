from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book
from orders.models import Cart, CartItem, Order

from orders.services import CartService, OrderService

from .serializers import (
    BookSerializer,
    CartSerializer,
    CartAddSerializer,
    CartItemUpdateSerializer,
    OrderSerializer,
    OrderCreateSerializer,
)

from .permissions import IsAdminOrReadOnly



class BookListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = Book.objects.all()

    serializer_class = BookSerializer

    permission_classes = [
        IsAdminOrReadOnly
    ]


class BookDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Book.objects.all()

    serializer_class = BookSerializer

    permission_classes = [
        IsAdminOrReadOnly
    ]

class CartAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        cart = CartService.get_or_create_cart(
            request.user
        )

        serializer = CartSerializer(cart)

        return Response(
            serializer.data
        )

class CartAddAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = CartAddSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        book_id = serializer.validated_data[
            'book_id'
        ]

        quantity = serializer.validated_data[
            'quantity'
        ]

        book = get_object_or_404(
            Book,
            id=book_id,
            is_active=True
        )

        try:

            CartService.add_to_cart(
                user=request.user,
                book=book,
                quantity=quantity
            )

        except ValidationError as e:

            return Response(
                {
                    'detail': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = CartService.get_or_create_cart(
            request.user
        )

        response_serializer = CartSerializer(
            cart
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

class CartItemUpdateAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def patch(self, request, item_id):

        serializer = CartItemUpdateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        quantity = serializer.validated_data[
            'quantity'
        ]

        try:

            CartService.update_quantity(
                user=request.user,
                cart_item_id=item_id,
                quantity=quantity
            )

        except ValidationError as e:

            return Response(
                {
                    'detail': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = CartService.get_or_create_cart(
            request.user
        )

        response_serializer = CartSerializer(
            cart
        )

        return Response(
            response_serializer.data
        )

class CartItemDeleteAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def delete(self, request, item_id):

        try:

            CartService.remove_from_cart(
                user=request.user,
                cart_item_id=item_id
            )

        except ValidationError as e:

            return Response(
                {
                    'detail': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'detail':
                'Item berhasil dihapus.'
            },
            status=status.HTTP_204_NO_CONTENT
        )

class OrderCreateAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = OrderCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        order_data = serializer.validated_data

        try:

            order = OrderService.create_order(
                user=request.user,
                full_name=order_data[
                    'full_name'
                ],
                phone=order_data[
                    'phone'
                ],
                address=order_data[
                    'address'
                ]
            )

        except ValidationError as e:

            return Response(
                {
                    'detail': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        response_serializer = OrderSerializer(
            order
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

class OrderListAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        orders = Order.objects.filter(
            user=request.user
        ).order_by('-created_at')

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            serializer.data
        )

class OrderDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, order_number):

        order = get_object_or_404(
            Order.objects.prefetch_related(
                'items'
            ),
            order_number=order_number,
            user=request.user
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data
        )