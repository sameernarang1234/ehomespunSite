# Generated by Django 3.2.4 on 2021-07-22 07:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0020_alter_store_membership_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='membership_start_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
