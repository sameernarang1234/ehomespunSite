# Generated by Django 3.2.4 on 2021-07-24 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0033_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='product_quantity',
            field=models.IntegerField(default=0),
        ),
    ]
