from rest_framework import serializers

from books.models import Book


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