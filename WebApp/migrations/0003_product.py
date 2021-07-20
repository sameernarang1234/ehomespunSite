# Generated by Django 3.2.4 on 2021-07-17 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0002_userdatabase'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('price', models.CharField(max_length=10)),
                ('currency', models.CharField(max_length=5)),
                ('shipping', models.CharField(max_length=50)),
                ('tags', models.CharField(max_length=100)),
                ('seller_id', models.IntegerField()),
                ('category_id', models.IntegerField()),
                ('sub_category_id', models.IntegerField()),
            ],
        ),
    ]