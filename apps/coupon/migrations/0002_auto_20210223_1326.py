# Generated by Django 3.1.6 on 2021-02-23 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='num_available',
            field=models.IntegerField(default=1),
        ),
    ]
