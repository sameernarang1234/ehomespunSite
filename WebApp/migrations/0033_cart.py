# Generated by Django 3.2.4 on 2021-07-24 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0032_alter_usercomment_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('buyer_id', models.IntegerField(default=0)),
                ('product_id', models.IntegerField(default=0)),
                ('product_quantity', models.IntegerField(default=1)),
            ],
        ),
    ]