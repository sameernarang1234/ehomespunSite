# Generated by Django 3.2.4 on 2021-07-24 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0036_buyeraddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyerBillingAddress',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(default=0)),
                ('first_name', models.CharField(default='', max_length=50)),
                ('last_name', models.CharField(default='', max_length=50)),
                ('company_name', models.CharField(default='', max_length=50)),
                ('country', models.CharField(default='', max_length=20)),
                ('address', models.CharField(default='', max_length=500)),
                ('city', models.CharField(default='', max_length=50)),
                ('state', models.CharField(default='', max_length=50)),
                ('postcode', models.CharField(default='', max_length=50)),
                ('phone', models.CharField(default='', max_length=20)),
                ('email', models.CharField(default='', max_length=50)),
            ],
        ),
    ]
