# Generated by Django 3.2.4 on 2021-07-21 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0011_rename_storecity_storestate'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='seller_id',
            field=models.IntegerField(default=0),
        ),
    ]
