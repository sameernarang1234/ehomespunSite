from django.db import models
import datetime

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
    username = models.CharField(max_length=50, default='')
    email = models.CharField(max_length=50, default="")
    user_type = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.username

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="")
    description = models.TextField(default="")
    short_description = models.TextField(default="")
    category_id = models.IntegerField(default=0)
    image1 = models.ImageField(upload_to="product/images",  default="")
    image2 = models.ImageField(upload_to="product/images",  default="")
    image3 = models.ImageField(upload_to="product/images",  default="")
    type = models.CharField(max_length=50, default="")
    price = models.CharField(max_length=10, default="")
    sale_price = models.CharField(max_length=10, default="")
    tax_status = models.CharField(max_length=20, default="")
    tax_class = models.CharField(max_length=20, default="")
    stock_status = models.CharField(max_length=20, default="In Stock")
    currency = models.CharField(max_length=5,  default="$")
    seller_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Store(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="")
    description = models.TextField(default="")
    seller_info = models.TextField(default="")
    url = models.CharField(max_length=100, default="")
    phone = models.CharField(max_length=20, default="")
    country = models.CharField(max_length=50, default="")
    address = models.TextField(default="")
    city = models.CharField(max_length=50, default="")
    state = models.CharField(max_length=50, default="")
    postal_code = models.CharField(max_length=10, default="")
    seller_id = models.IntegerField(default=0)
    store_banner = models.ImageField(upload_to="store/images",  default="")
    store_icon = models.ImageField(upload_to="store/images", default="")
    terms_and_conditions = models.TextField(default="")
    twitter_username = models.CharField(max_length=50, default="")
    instagram_username = models.CharField(max_length=50, default="")
    facebook_url = models.CharField(max_length=100, default="")
    linkedin_url = models.CharField(max_length=100, default="")
    youtube_url = models.CharField(max_length=100, default="")
    pinterest_url = models.CharField(max_length=100, default="")
    snapchat_username = models.CharField(max_length=50, default="")
    telegram_username = models.CharField(max_length=50, default="")
    membership_status = models.CharField(max_length=50, default="inactive")
    membership_type = models.CharField(max_length=100, default="")
    membership_start_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.name

class StoreState(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class SellerPaymentDetail(models.Model):
    seller_id = models.IntegerField(primary_key=True, default=0)
    paypal_client_id = models.CharField(max_length=500, default="")
    stripe_public_key = models.CharField(max_length=500, default="")
    stripe_private_key = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.seller_id

class Shipping(models.Model):
    seller_id = models.IntegerField(primary_key=True, default=0)
    shipping_type = models.CharField(max_length=30, default="")
    national_shipping_fee = models.CharField(default="", max_length=10)
    national_free_shipping_fee = models.CharField(default="", max_length=10)
    national_free_shipping_enabled = models.CharField(max_length=5, default="")
    disable_national_shipping = models.CharField(max_length=5, default="")
    international_shipping_fee = models.CharField(default="", max_length=10)
    international_free_shipping_fee = models.CharField(default="", max_length=10)
    international_free_shipping_enabled = models.CharField(max_length=5, default="")
    disable_international_shipping = models.CharField(max_length=5, default="")
    product_handling_fee = models.CharField(max_length=10, default="")
    shipping_country = models.CharField(max_length=20, default="")
    shipping_address = models.CharField(max_length=500, default="")
    shipping_city = models.CharField(max_length=20, default="")
    shipping_state = models.CharField(max_length=20, default="")
    shipping_postcode = models.CharField(max_length=10, default="")


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.IntegerField(default=0)
    seller_id = models.IntegerField(default=0)
    buyer_id = models.IntegerField(default=0)
    tax = models.CharField(max_length=10, default="")
    price = models.CharField(max_length=10, default="")

    def __str__(self):
        return self.id
