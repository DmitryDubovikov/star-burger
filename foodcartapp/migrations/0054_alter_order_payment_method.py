# Generated by Django 4.2 on 2023-05-22 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_rename_registrated_at_order_registered_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('ON', 'Онлайн'), ('CA', 'Наличными')], max_length=2),
        ),
    ]
