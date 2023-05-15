from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderItemListSerializer(serializers.ListSerializer):
    child = OrderItemSerializer()


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "firstname",
            "lastname",
            "phonenumber",
            "address",
            "products",
        ]
        read_only_fields = ("id",)
        # write_only_fields = ("products",)
