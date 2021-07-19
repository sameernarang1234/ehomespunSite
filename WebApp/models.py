from django.db import models

# Create your models here.
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category_id = models.IntegerField()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class UserDatabase(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    user_type = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="")
    description = models.TextField(default="")
    short_description = models.TextField(default="")
    type = models.CharField(max_length=50, default="")
    inventory = models.IntegerField(default=0)
    price = models.CharField(max_length=10, default="")
    sale_price = models.CharField(max_length=10, default="")
    tax_status = models.CharField(max_length=20, default="")
    tax_class = models.CharField(max_length=20, default="")
    currency = models.CharField(max_length=5,  default="")
    shipping = models.CharField(max_length=50, default="")
    tags = models.CharField(max_length=100, default="")
    seller_id = models.IntegerField(default=0)
    category_id = models.IntegerField(default=0)
    sub_category_id = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class StoreCity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name