from rest_framework import serializers
from .models import Customer, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "label", "street", "city", "state", "postal_code", "country", "is_default", "created_at"]
        read_only_fields = ["id", "created_at"]


class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "email", "first_name", "last_name", "phone", "is_active", "created_at", "addresses"]
        read_only_fields = ["id", "user_id", "created_at"]


class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["user_id", "email", "first_name", "last_name", "phone"]
