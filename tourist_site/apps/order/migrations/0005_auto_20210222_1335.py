# Generated by Django 3.1.6 on 2021-02-22 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_order_used_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='used_coupon',
            field=models.IntegerField(default=0),
        ),
    ]
