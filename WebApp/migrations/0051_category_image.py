# Generated by Django 3.2.4 on 2021-07-31 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0050_supportrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(default='', upload_to='category/images'),
        ),
    ]
