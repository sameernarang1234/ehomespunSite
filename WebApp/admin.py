from django.contrib import admin
from .models import Category, SubCategory, UserDatabase, Product, StoreCity

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(UserDatabase)
admin.site.register(Product)
admin.site.register(StoreCity)