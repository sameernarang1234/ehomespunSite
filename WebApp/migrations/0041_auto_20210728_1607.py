# Generated by Django 3.2.4 on 2021-07-28 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0040_auto_20210728_1505'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='price',
            new_name='product_price',
        ),
        migrations.RemoveField(
            model_name='adminpaymentdetail',
            name='seller_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='seller_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='tax',
        ),
        migrations.AddField(
            model_name='adminpaymentdetail',
            name='id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='order',
            name='buyer_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='order',
            name='currency',
            field=models.CharField(default='$', max_length=5),
        ),
        migrations.AddField(
            model_name='order',
            name='product_category_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='order',
            name='product_description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='product_image1',
            field=models.ImageField(default='', upload_to='product/images'),
        ),
        migrations.AddField(
            model_name='order',
            name='product_image2',
            field=models.ImageField(default='', upload_to='product/images'),
        ),
        migrations.AddField(
            model_name='order',
            name='product_image3',
            field=models.ImageField(default='', upload_to='product/images'),
        ),
        migrations.AddField(
            model_name='order',
            name='product_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='product_sale_price',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='order',
            name='product_short_description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='product_tax_class',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='product_tax_status',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='product_type',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='total_cost',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='total_tax',
            field=models.IntegerField(default=0),
        ),
    ]