from django.db import models
import datetime

# Create your models here.
class SupportRequest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="")
    email = models.CharField(max_length=50, default="")
    subject = models.CharField(max_length=50, default="")
    description = models.TextField(default="")
    image = models.ImageField(upload_to="support/images", default="")
    category = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="category/images", default="")

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
    user_type = models.CharField(max_length=50, default="BUYER")

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
    sales = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class StoreState(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class SellerPaymentDetail(models.Model):
    seller_id = models.IntegerField(primary_key=True, default=0)
    paypal_address = models.CharField(max_length=50, default='')
    bank_account_name = models.CharField(max_length=50, default='')
    bank_account_number = models.CharField(max_length=50, default="")
    bank_name = models.CharField(max_length=50, default="")
    bank_routing_number = models.CharField(max_length=50, default="")
    bank_IBAN = models.CharField(max_length=50, default="")
    bank_BIC_SWIFT = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.paypal_address

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

    def __str__(self):
        return str(self.seller_id)

class Coupon(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, default="")
    description = models.TextField(default="")
    discount_type = models.CharField(max_length=50, default="")
    apply_to_all_products = models.BooleanField(default=False)
    coupon_amount = models.CharField(max_length=10)
    allow_free_shipping = models.BooleanField(default=False)
    coupon_expiry = models.DateField(default=datetime.date.today)
    minimum_spend = models.CharField(max_length=10, default="")
    maximum_spend = models.CharField(max_length=10, default="")
    individual_use_only = models.BooleanField(default=False)
    exclude_sale_item = models.BooleanField(default=False)
    restricted_emails = models.CharField(max_length=500, default="")
    usage_limit_per_coupon = models.IntegerField(default=100)
    usage_limit_item = models.IntegerField(default=100)
    usage_limit_per_user = models.IntegerField(default=100)

    seller_id = models.IntegerField(default=0)

    def __str__(self):
        return self.code

class UserComment(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.IntegerField(default=0)
    username = models.CharField(default="", max_length=100)
    comment = models.CharField(max_length=100, default="")

    def __str__(self):
        return str(self.product_id)

class UserReview(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return str(self.product_id)

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    buyer_id = models.IntegerField(default=0)
    product_id = models.IntegerField(default=0)
    product_quantity = models.IntegerField(default=0)

    def __str__(self):
        return str(self.buyer_id)

class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    buyer_id = models.IntegerField(default=0)
    product_id = models.IntegerField(default=0)

    def __str__(self):
        return str(self.buyer_id)

class BuyerAddress(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default=0)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    company_name = models.CharField(max_length=50, default="")
    country = models.CharField(max_length=20, default="")
    address = models.CharField(max_length=500, default="")
    city = models.CharField(max_length=50, default="")
    state = models.CharField(max_length=50, default="")
    postcode = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=20, default="")
    email = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.first_name

class BuyerBillingAddress(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default=0)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    company_name = models.CharField(max_length=50, default="")
    country = models.CharField(max_length=20, default="")
    address = models.CharField(max_length=500, default="")
    city = models.CharField(max_length=50, default="")
    state = models.CharField(max_length=50, default="")
    postcode = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=20, default="")
    email = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.first_name

class AdminPaymentDetail(models.Model):
    id = models.AutoField(primary_key=True, default=1)
    stripe_public_key = models.CharField(max_length=500, default="")
    stripe_private_key = models.CharField(max_length=500, default="")

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    seller_id = models.IntegerField(default=0)
    seller_name = models.CharField(default="", max_length=50)
    seller_paypal = models.CharField(default="", max_length=100)
    buyer_id = models.IntegerField(default=0)
    buyer_name = models.CharField(max_length=50, default="")
    product_id = models.IntegerField(default=0)
    product_name = models.CharField(max_length=100, default="")
    product_description = models.TextField(default="")
    product_short_description = models.TextField(default="")
    product_category_name = models.CharField(max_length=50, default="")
    product_image1 = models.ImageField(upload_to="product/images",  default="")
    product_image2 = models.ImageField(upload_to="product/images",  default="")
    product_image3 = models.ImageField(upload_to="product/images",  default="")
    product_type = models.CharField(max_length=50, default="")
    product_price = models.CharField(max_length=10, default="")
    product_sale_price = models.CharField(max_length=10, default="")
    product_tax_status = models.CharField(max_length=20, default="")
    product_tax_class = models.CharField(max_length=20, default="")
    currency = models.CharField(max_length=5,  default="$")
    quantity = models.IntegerField(default=0)
    total_tax = models.CharField(default="", max_length=10)
    total_cost = models.IntegerField(default=0)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    country = models.CharField(max_length=50, default="")
    address = models.TextField(default="")
    state = models.CharField(max_length=50, default="")
    city = models.CharField(max_length=50, default="")
    postcode = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=50, default="")
    email = models.CharField(max_length=50, default="")
    refund_status = models.CharField(max_length=50, default="")
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.buyer_name

class AdminTaxRules(models.Model):
    id = models.AutoField(primary_key=True)
    standard_class_tax_percentage = models.CharField(max_length=10, default="")
    reduced_rate_class_tax_percentage = models.CharField(max_length=10, default="")

    def __str__(self):
        return "Tax Percentage"

class BuyerState(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(default="", max_length=50)

    def __str__(self):
        return self.name

class MembershipPrice(models.Model):
    annual_membership_price = models.CharField(max_length=10, default="9.99")
    monthly_membership_price = models.CharField(max_length=10, default="4.99")

    def __str__(self):
        return "Membership Price"

class GuestCart(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.IntegerField(default=0)
    product_quantity = models.IntegerField(default=0)
    session_id = models.IntegerField(default=0)

    def __str__(self):
        return str(self.buyer_id)
