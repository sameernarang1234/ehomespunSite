# Generated by Django 3.2.4 on 2021-07-21 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0010_store'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StoreCity',
            new_name='StoreState',
        ),
    ]
