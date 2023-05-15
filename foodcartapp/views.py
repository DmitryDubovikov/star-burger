import json
from django.http import JsonResponse
from django.templatetags.static import static
from django.http import HttpResponseBadRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderItem


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


@api_view(["POST"])
def register_order(request):
    if request.method == "POST":
        data = request.data

        products_list = data.get("products")
        if products_list == None:
            return Response(
                {
                    "message": "не пустой список продуктов обязателен для формирования заказа, "
                    "данные по ключу products не переданы!"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif not isinstance(products_list, list):
            return Response(
                {
                    "message": "не пустой список продуктов обязателен для формирования заказа, "
                    "данные по ключу products не являются списком!"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif len(products_list) == 0:
            return Response(
                {
                    "message": "не пустой список продуктов обязателен для формирования заказа, "
                    "переданный список продуктов пуст!"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            for p in products_list:
                try:
                    obj = Product.objects.get(pk=p["product"])
                except Product.DoesNotExist:
                    id = p["product"]
                    return Response(
                        {"message": f"продукт c id {id} не найден!"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        firstname = data.get("firstname")
        lastname = data.get("lastname")
        phonenumber = data.get("phonenumber")
        address = data.get("address")

        if firstname == None or not isinstance(firstname, str) or firstname == "":
            return Response(
                {"message": "имя должно быть не пустой строкой!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if lastname == None or not isinstance(lastname, str) or lastname == "":
            return Response(
                {"message": "фамилия должна быть не пустой строкой!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if address == None or not isinstance(address, str) or address == "":
            return Response(
                {"message": "адрес должен быть не пустой строкой!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_order = Order(
            first_name=firstname,
            last_name=lastname,
            phone_number=phonenumber,
            address=address,
        )
        new_order.save()

        for p in products_list:
            new_item = OrderItem(
                order=new_order,
                product=Product.objects.get(id=p["product"]),
                quantity=p["quantity"],
            )
            new_item.save()

        return JsonResponse(data)

    else:
        return HttpResponseBadRequest("Invalid request method")
