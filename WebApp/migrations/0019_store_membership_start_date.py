# Generated by Django 3.2.4 on 2021-07-22 07:33

from django.db import migrations, models
from datetime import date


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0018_store_membership_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='membership_start_date',
            field=models.DateField(default=date.today),
        ),
    ]
