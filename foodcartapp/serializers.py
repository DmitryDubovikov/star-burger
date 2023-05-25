from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

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

    def create(self, validated_data):
        new_order = Order.objects.create(
            firstname=validated_data["firstname"],
            lastname=validated_data["lastname"],
            phonenumber=validated_data["phonenumber"],
            address=validated_data["address"],
        )

        for item in validated_data["products"]:
            product = item["product"]
            OrderItem.objects.create(
                order=new_order,
                product=product,
                price=product.price,
                quantity=item["quantity"],
            )

        return new_order
