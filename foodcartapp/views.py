from django.http import JsonResponse
from django.templatetags.static import static

import json
from django.http import HttpResponseBadRequest
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


def register_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            new_order = Order(
                first_name=data["firstname"],
                last_name=data["lastname"],
                phone_number=data["phonenumber"],
                address=data["address"],
            )
            new_order.save()

            for p in data["products"]:
                new_item = OrderItem(
                    order=new_order,
                    product=Product.objects.get(id=p["product"]),
                    quantity=p["quantity"],
                )
                new_item.save()

            return JsonResponse(data)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    else:
        return HttpResponseBadRequest("Invalid request method")

    return JsonResponse({})
