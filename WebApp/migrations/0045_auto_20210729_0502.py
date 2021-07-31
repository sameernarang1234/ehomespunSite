# Generated by Django 3.2.4 on 2021-07-29 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0044_admintaxrules'),
    ]

    operations = [
        migrations.RenameField(
            model_name='admintaxrules',
            old_name='tax_percentage',
            new_name='standard_class_tax_percentage',
        ),
        migrations.AddField(
            model_name='admintaxrules',
            name='reduced_rate_class_tax_percentage',
            field=models.CharField(default='', max_length=10),
        ),
    ]