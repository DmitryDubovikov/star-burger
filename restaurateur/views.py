from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.conf import settings

import requests
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, OrderItem
from placesapp.models import Place


class Login(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Укажите имя пользователя"}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={"form": form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request,
            "login.html",
            context={
                "form": form,
                "ivalid": True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("restaurateur:login")


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_products(request):
    restaurants = list(Restaurant.objects.order_by("name"))
    products = list(Product.objects.prefetch_related("menu_items"))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False) for restaurant in restaurants
        ]

        products_with_restaurant_availability.append((product, ordered_availability))

    return render(
        request,
        template_name="products_list.html",
        context={
            "products_with_restaurant_availability": products_with_restaurant_availability,
            "restaurants": restaurants,
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={
            "restaurants": Restaurant.objects.all(),
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_orders(request):
    orders = (
        Order.objects_decorated.exclude(status="CL")
        .order_by("status")
        .prefetch_related("restaurant")
    )

    orders_list = list(orders.values_list("id", flat=True))

    filters = Q()
    for value in orders_list:
        filters |= Q(order=value)

    # оставляем только строки заказов orders
    order_items = OrderItem.objects.filter(filters).prefetch_related("product")

    availability = dict()
    for el in (
        RestaurantMenuItem.objects.filter(availability=True)
        .order_by("product")
        .prefetch_related("product")
        .prefetch_related("restaurant")
    ):
        if el.product in availability.keys():
            availability[el.product].append(el.restaurant)
        else:
            availability[el.product] = [el.restaurant]

    context_data = []
    for order in orders:
        rests_info = ""
        if order.restaurant:
            rests_info = f"Готовит {order.restaurant}"
        else:
            order_aviability = []
            for item in order_items.filter(order=order):
                order_aviability.append(set(availability[item.product]))
            rests = [
                {"rest": r, "dist": 0} for r in set.intersection(*order_aviability)
            ]

            if len(rests) == 0:
                rests_info = "Невозможно приготовить ни в одном ресторане"
            else:
                for r in rests:
                    r["dist"] = calc_distance(r["rest"].address, order.address)

                sorted_rests = sorted(
                    rests, key=lambda x: x["dist"] if x["dist"] else 999999
                )

                rests_info = "Может быть приготовлен ресторанами: "
                for el in sorted_rests:
                    rests_info += f"{el['rest']} \
                        ({'не определено ' if el['dist'] == None else el['dist'] } км) \n"

        context_data.append({"order": order, "rests_info": rests_info})

    return render(
        request,
        template_name="order_items.html",
        context={"context_data": context_data},
    )


def calc_distance(adress1, adress2):
    coord1 = fetch_coordinates(adress1)
    coord2 = fetch_coordinates(adress2)

    if not coord1 or not coord2:
        return None

    # taking pair of (lat, lon) tuples
    return round(
        distance.distance((coord1[1], coord1[0]), (coord2[1], coord2[0])).km, 3
    )


def fetch_coordinates(address):
    apikey = settings.YANDEX_GEOCODER_API_KEY

    place = Place.objects.filter(address=address)
    if len(place) > 0:
        return place[0].lon, place[0].lat

    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")

    new_place = Place(address=address, lon=lon, lat=lat)
    new_place.save()

    return lon, lat
