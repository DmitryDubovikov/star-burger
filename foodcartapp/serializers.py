from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderItemListSerializer(serializers.ListSerializer):
    child = OrderItemSerializer()


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(allow_empty=False)

    class Meta:
        model = Order
        fields = [
            "firstname",
            "lastname",
            "phonenumber",
            "address",
            "products",
        ]
