import json
from django.http import JsonResponse
from django.templatetags.static import static
from django.http import HttpResponseBadRequest
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderItem
from .serializers import OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse(
        [
            {
                "title": "Burger",
                "src": static("burger.jpg"),
                "text": "Tasty Burger at your door step",
            },
            {
                "title": "Spices",
                "src": static("food.jpg"),
                "text": "All Cuisines",
            },
            {
                "title": "New York",
                "src": static("tasty.jpg"),
                "text": "Food is incomplete without a tasty dessert",
            },
        ],
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


def product_list_api(request):
    products = Product.objects.select_related("category").available()

    dumped_products = []
    for product in products:
        dumped_product = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "special_status": product.special_status,
            "description": product.description,
            "category": {
                "id": product.category.id,
                "name": product.category.name,
            }
            if product.category
            else None,
            "image": product.image.url,
            "restaurant": {
                "id": product.id,
                "name": product.name,
            },
        }
        dumped_products.append(dumped_product)
    return JsonResponse(
        dumped_products,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


@transaction.atomic
@api_view(["POST"])
def register_order(request):
    order_serializer = OrderSerializer(data=request.data)
    if order_serializer.is_valid(raise_exception=True):
        new_order = order_serializer.save()

        for item in order_serializer.validated_data["products"]:
            product = item["product"]
            new_item = OrderItem(
                order=new_order,
                product=product,
                price=product.price,
                quantity=item["quantity"],
            )
            new_item.save()

    return Response(OrderSerializer(new_order).data, status=status.HTTP_201_CREATED)
