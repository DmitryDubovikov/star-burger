from django.db import migrations


def fill_empty_prices(apps, schema_editor):
    # We can't import the OrderItem model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    OrderItem = apps.get_model("foodcartapp", "OrderItem")
    for item in OrderItem.objects.filter(price=0).select_related("product"):
        item.price = item.product.price
        item.save()


class Migration(migrations.Migration):
    dependencies = [
        ("foodcartapp", "0043_alter_orderitem_quantity"),
    ]

    operations = [
        migrations.RunPython(fill_empty_prices),
    ]
