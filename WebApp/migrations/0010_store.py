# Generated by Django 3.2.4 on 2021-07-21 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0009_auto_20210721_1037'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=50)),
                ('description', models.TextField(default='')),
                ('seller_info', models.TextField(default='')),
                ('url', models.CharField(default='', max_length=100)),
                ('phone', models.CharField(default='', max_length=20)),
                ('country', models.CharField(default='', max_length=50)),
                ('address', models.TextField(default='')),
                ('city', models.CharField(default='', max_length=50)),
                ('state', models.CharField(default='', max_length=50)),
                ('postal_code', models.CharField(default='', max_length=10)),
            ],
        ),
    ]
