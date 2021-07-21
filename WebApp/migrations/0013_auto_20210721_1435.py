# Generated by Django 3.2.4 on 2021-07-21 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0012_store_seller_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellerPaymentDetail',
            fields=[
                ('seller_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('paypal_client_id', models.CharField(default='', max_length=500)),
                ('stripe_public_key', models.CharField(default='', max_length=500)),
                ('stripe_private_key', models.CharField(default='', max_length=500)),
            ],
        ),
        migrations.AddField(
            model_name='store',
            name='store_banner',
            field=models.ImageField(default='', upload_to='store/images'),
        ),
        migrations.AddField(
            model_name='store',
            name='store_icon',
            field=models.ImageField(default='', upload_to='store/images'),
        ),
    ]
