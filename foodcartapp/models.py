from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField("название", max_length=50)
    address = models.CharField(
        "адрес",
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        "контактный телефон",
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = "ресторан"
        verbose_name_plural = "рестораны"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(availability=True).values_list(
            "product"
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField("название", max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("название", max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="категория",
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        "цена", max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField("картинка")
    special_status = models.BooleanField(
        "спец.предложение",
        default=False,
        db_index=True,
    )
    description = models.TextField(
        "описание",
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name


class RestaurantMenuItemDecoratedManager(models.Manager):
    def get_queryset(self):
        return (
            RestaurantMenuItem.objects.filter(availability=True)
            .order_by("product")
            .prefetch_related("product")
            .prefetch_related("restaurant")
        )


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="menu_items",
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name="продукт",
    )
    availability = models.BooleanField("в продаже", default=True, db_index=True)

    objects = models.Manager()  # The default manager.
    objects_decorated = RestaurantMenuItemDecoratedManager()  # Our custom manager.

    class Meta:
        verbose_name = "пункт меню ресторана"
        verbose_name_plural = "пункты меню ресторана"
        unique_together = [["restaurant", "product"]]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderDecoratedManager(models.Manager):
    def get_queryset(self):
        return Order.objects.annotate(
            total_sum=Sum(F("items__quantity") * F("items__price"))
        )


class Order(models.Model):
    NEW = "NE"
    IN_RESTAURANT = "RE"
    IN_DELIVERY = "DE"
    CLOSED = "CL"
    STATUS_CHOICES = [
        (NEW, "New"),
        (IN_RESTAURANT, "In restaurant"),
        (IN_DELIVERY, "In delivery"),
        (CLOSED, "Closed"),
    ]

    ONLINE = "ON"
    CASH = "CA"
    PAYMENT_METHODS = [(ONLINE, "Онлайн"), (CASH, "Наличными")]

    firstname = models.CharField(max_length=100, blank=False, verbose_name="Имя")
    lastname = models.CharField(max_length=100, blank=False, verbose_name="Фамилия")
    phonenumber = PhoneNumberField(verbose_name="Телефон")
    address = models.CharField(max_length=100, blank=False, verbose_name="Адрес")
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=NEW,
    )
    comment = models.TextField(blank=True)
    registered_at = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(
        max_length=2, choices=PAYMENT_METHODS, blank=False
    )
    restaurant = models.ForeignKey(
        Restaurant, null=True, blank=True, on_delete=models.CASCADE
    )

    objects = models.Manager()  # The default manager.
    objects_decorated = OrderDecoratedManager()  # Our custom manager.

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        indexes = [
            models.Index(fields=["firstname"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Заказ {self.id} от {self.firstname} {self.lastname}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="продукт",
    )
    quantity = models.IntegerField(
        verbose_name="количество", validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        "цена",
        max_digits=8,
        decimal_places=2,
        blank=False,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "элемент заказа"
        verbose_name_plural = "элементы заказа"
        unique_together = [["order", "product"]]
