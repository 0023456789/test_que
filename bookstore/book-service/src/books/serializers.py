from rest_framework import serializers
from .models import Book, Category, Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "bio", "created_at"]
        read_only_fields = ["id", "created_at"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "parent"]
        read_only_fields = ["id"]


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Author.objects.all(), write_only=True, source="authors"
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    available_quantity = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = [
            "id", "title", "isbn", "description", "price",
            "cover_image_url", "publisher", "published_date", "language", "pages",
            "category", "category_name", "authors", "author_ids",
            "stock_quantity", "reserved_quantity", "available_quantity",
            "average_rating", "total_reviews",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "average_rating", "total_reviews"]


class BookListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    available_quantity = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = [
            "id", "title", "isbn", "price", "cover_image_url",
            "category_name", "available_quantity",
            "average_rating", "total_reviews", "is_active",
        ]


class InventoryUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    operation = serializers.ChoiceField(choices=["add", "subtract", "set"])
