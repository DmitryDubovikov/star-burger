# Generated by Django 4.2 on 2023-05-15 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_order_phone_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='last_name',
            new_name='lastname',
        ),
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(max_length=100, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='foodcartapp.order', verbose_name='заказ'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['firstname'], name='foodcartapp_firstna_6b6263_idx'),
        ),
    ]
