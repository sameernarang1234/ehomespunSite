# Generated by Django 3.2.4 on 2021-07-22 08:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0023_remove_store_membership_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='membership_start_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
