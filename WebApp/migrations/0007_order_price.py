# Generated by Django 3.2.4 on 2021-07-20 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0006_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.CharField(default='', max_length=10),
        ),
    ]
