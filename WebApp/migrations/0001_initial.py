# Generated by Django 3.2.4 on 2021-07-17 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='subCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category_id', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
            ],
        ),
    ]