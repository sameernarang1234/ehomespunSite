from django.contrib import admin
from .models import Category, SubCategory, UserDatabase, Product, StoreState, Order, Store, SellerPaymentDetail, Shipping, Coupon, UserReview, UserComment, Cart, Wishlist, BuyerAddress, BuyerBillingAddress

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(UserDatabase)
admin.site.register(Product)
admin.site.register(StoreState)
admin.site.register(Order)
admin.site.register(Store)
admin.site.register(SellerPaymentDetail)
admin.site.register(Shipping)
admin.site.register(Coupon)
admin.site.register(UserComment)
admin.site.register(UserReview)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(BuyerAddress)
admin.site.register(BuyerBillingAddress)
