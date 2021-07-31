from rest_framework import serializers
from .models import Category, SubCategory, UserDatabase, Product, StoreState, Store, SellerPaymentDetail, Shipping, Coupon, UserReview, UserComment, Cart, Wishlist, BuyerBillingAddress, BuyerAddress, AdminPaymentDetail, Order, AdminTaxRules, BuyerState, MembershipPrice, SupportRequest

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class UserDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDatabase
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class StoreStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreState
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class SellerPaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerPaymentDetail
        fields = '__all__'

class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReview
        fields = '__all__'

class UserCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserComment
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'

class BuyerBillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerBillingAddress
        fields = '__all__'

class BuyerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerAddress
        fields = '__all__'

class AdminPaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPaymentDetail
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AdminTaxRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminTaxRules
        fields = '__all__'

class BuyerStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerState
        fields = '__all__'

class MembershipPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPrice
        fields = '__all__'

class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = '__all__'