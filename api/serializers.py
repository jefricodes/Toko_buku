import re

from rest_framework import serializers

from books.models import Book
from orders.models import (
    Cart,
    CartItem,
    Order,
    OrderItem
)


class BookSerializer(serializers.ModelSerializer):

    class Meta:

        model = Book

        fields = [
            'id',
            'category',
            'title',
            'author',
            # 'publisher',
            # 'isbn',
            'description',
            'price',
            'stock',
            'cover',
            'is_active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def validate_price(self, value):

        if value < 0:

            raise serializers.ValidationError(
                'Harga tidak boleh negatif.'
            )

        return value

    def validate_stock(self, value):

        if value < 0:

            raise serializers.ValidationError(
                'Stok tidak boleh negatif.'
            )

        return value


class CartItemSerializer(
    serializers.ModelSerializer
):

    book_title = serializers.CharField(
        source='book.title',
        read_only=True
    )

    price = serializers.DecimalField(
        source='book.price',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:

        model = CartItem

        fields = [
            'id',
            'book',
            'book_title',
            'price',
            'quantity',
            'subtotal',
        ]

        read_only_fields = [
            'id',
            'book_title',
            'price',
            'subtotal',
        ]

    def get_subtotal(self, obj):

        return obj.get_subtotal()


class CartSerializer(
    serializers.ModelSerializer
):

    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    total = serializers.SerializerMethodField()

    class Meta:

        model = Cart

        fields = [
            'id',
            'items',
            'total',
        ]

        read_only_fields = [
            'id',
            'items',
            'total',
        ]

    def get_total(self, obj):

        return obj.get_total()


class CartAddSerializer(
    serializers.Serializer
):

    book_id = serializers.IntegerField()

    quantity = serializers.IntegerField(
        min_value=1,
        default=1
    )


class CartItemUpdateSerializer(
    serializers.Serializer
):

    quantity = serializers.IntegerField(
        min_value=1
    )


class OrderItemSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = OrderItem

        fields = [
            'id',
            'book',
            'book_title',
            'price',
            'quantity',
            'subtotal',
        ]

        read_only_fields = [
            'id',
            'book',
            'book_title',
            'price',
            'quantity',
            'subtotal',
        ]


class OrderSerializer(
    serializers.ModelSerializer
):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = Order

        fields = [
            'id',
            'order_number',
            'full_name',
            'phone',
            'address',
            'total',
            'status',
            'created_at',
            'updated_at',
            'items',
        ]

        read_only_fields = [
            'id',
            'order_number',
            'total',
            'status',
            'created_at',
            'updated_at',
            'items',
        ]


class OrderCreateSerializer(
    serializers.Serializer
):

    full_name = serializers.CharField(
        max_length=150,
        trim_whitespace=True
    )

    phone = serializers.CharField(
        max_length=30,
        trim_whitespace=True
    )

    address = serializers.CharField(
        trim_whitespace=True
    )

    def validate_full_name(self, value):

        if not value.strip():

            raise serializers.ValidationError(
                'Nama lengkap wajib diisi.'
            )

        return value

    def validate_phone(self, value):

        phone = value.replace(
            ' ',
            ''
        )

        if not re.match(
            r'^[0-9+\-()]+$',
            phone
        ):

            raise serializers.ValidationError(
                'Nomor telepon tidak valid.'
            )

        return phone

    def validate_address(self, value):

        if not value.strip():

            raise serializers.ValidationError(
                'Alamat wajib diisi.'
            )

        return value