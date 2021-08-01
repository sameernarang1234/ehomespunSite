from django.db.models.enums import IntegerChoices
from django.shortcuts import render, redirect

from .models import Category, SubCategory, UserDatabase, Product, StoreState, Store, SellerPaymentDetail, Shipping, Coupon, UserReview, UserComment, Cart, Wishlist, BuyerBillingAddress, BuyerAddress, AdminPaymentDetail, Order, AdminTaxRules, BuyerState, MembershipPrice, SupportRequest, GuestCart

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import date, timedelta

from .serializers import CategorySerializer, SubCategorySerializer, UserDatabaseSerializer, ProductSerializer, StoreStateSerializer, StoreSerializer, SellerPaymentDetailSerializer, ShippingSerializer, CouponSerializer, UserReviewSerializer, UserCommentSerializer, CartSerializer, WishlistSerializer, BuyerBillingAddressSerializer, BuyerAddressSerializer, AdminPaymentDetailSerializer, OrderSerializer, AdminTaxRulesSerializer, BuyerStateSerializer, MembershipPriceSerializer, SupportRequestSerializer

import stripe

from django.core.mail import send_mail

from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from random import random

# Create your views here.

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        userDB = UserDatabase.objects.get(email=user.email)
        user_type = userDB.user_type

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            "user_type": user_type
        })

def homePage(request):
    try:
        username = request.session["username"]
    except:
        username = None
    cart_total = 0.00
    if username is not None:
        print("INSIDE USERNAME")
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = float(cart_product.sale_price)
            cart_total += float(price * quantity)
        print(cart_total)

    categories = Category.objects.all()
    allProducts = Product.objects.all()

    products = []
    count = 0
    discount_products = []
    for product in allProducts:
        if count > 4:
            break
        products.append(product)
        count += 1
        print("PRICES")
        print(product.price)
        print(product.sale_price)
        price = float(product.price)
        sale_price = float(product.sale_price)
        if price != sale_price:
            discount_products.append(product)

    print(products)

    params = {
        "categories": categories,
        "products": products,
        "discount_products": discount_products,
        "cart_total": cart_total
    }
    return render(request, 'home.html', params)

@api_view(["GET"])
def homePageApi(request):
    user = request.user

    cart_total = 0.00
    if str(user) != "AnonymousUser":
        email = user.email
        userDB = UserDatabase.objects.get(email=email)
        buyer_id = userDB.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = float(cart_product.sale_price)
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    allProducts = Product.objects.all()

    serialized_products = ProductSerializer(allProducts, many=True)

    serialized_categories = CategorySerializer(categories, many=True)

    products = []
    count = 0
    for product in serialized_products.data:
        if count > 4:
            break
        products.append(product)
        count += 1

    return Response({
        "categories": serialized_categories.data,
        "products": products,
        "cart_total": cart_total
    })

def loginPage(request):
    try:
        username = request.session["username"]
    except:
        username = None
    cart_total = 0.00
    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'login.html', params)

@api_view(["GET"])
def loginPageApi(request):
    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "categories": serialized_categories
    })

def handleSignup(request):
    if request.method == 'POST':
        inputUsername = request.POST.get('username')
        inputEmail = request.POST.get('email')
        inputPassword = request.POST.get('password')
        isMerchantAccount = request.POST.get('isMerchantAccount')
        signupRemember = request.POST.get('signup-remember')

        userType = ""

        if (isMerchantAccount == "on"):
            userType = "MERCHANT"
        else:
            userType = "BUYER"

        user = User.objects.create_user(inputUsername, inputEmail, inputPassword)
        user.save()

        userDB = UserDatabase(
            username=inputUsername,
            email=inputEmail,
            user_type=userType
        )
        userDB.save()

        loggedInUser = authenticate(username=inputUsername, password=inputPassword)

        if loggedInUser is not None:
            login(request, loggedInUser)
            request.session["username"] = inputUsername
            if signupRemember == "on":
                request.session.set_expiry(86400)
            else:
                request.session.set_expiry(0)

            if (userType == "BUYER"):
                return redirect("userDashboard")
            else:
                return redirect("proDashboard")
    return redirect("loginPage")

def handleSignupApi(request):
    if request.method == 'POST':
        inputUsername = request.POST.get('username')
        inputEmail = request.POST.get('email')
        inputPassword = request.POST.get('password')
        isMerchantAccount = request.POST.get('isMerchantAccount')
        signupRemember = request.POST.get('signup-remember')

        userType = ""

        if (isMerchantAccount == "on"):
            userType = "MERCHANT"
        else:
            userType = "BUYER"

        user = User.objects.create_user(inputUsername, inputEmail, inputPassword)
        user.save()

        userDB = UserDatabase(
            username=inputUsername,
            email=inputEmail,
            user_type=userType
        )
        userDB.save()

        return Response({
            "status_code": 200,
            "message": "You have been successfully registered"
        })

def loginUser(request):
    if request.method == "POST":
        inputUsername = request.POST.get("username")
        inputPassword = request.POST.get("password")
        loginRemember = request.POST.get("login-remember")
        loggedInUser = authenticate(username=inputUsername, password=inputPassword)

        if loggedInUser is not None:
            login(request, loggedInUser)
            request.session["username"] = inputUsername
            if loginRemember == "on":
                request.session.set_expiry(86400*7)
            else:
                request.session.set_expiry(0)

            userDB = UserDatabase.objects.get(username=inputUsername)
            userType = userDB.user_type

            if userType == "MERCHANT":
                return redirect("proDashboard")
            else:
                return redirect("userDashboard")

    return redirect("loginPage")

def logoutUser(request):
    logout(request)
    try:
        del request.session["username"]
    except:
        print()
    return redirect("homePage")

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def logoutUserApi(request):
    user = request.user
    token = Token.objects.get(user=user)
    token.delete()

    return Response({
        "message": "You have been successfully logged out."
    })

def dashboard(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    user = UserDatabase.objects.get(username=username)
    userType = user.user_type

    if userType == "MERCHANT":
        return redirect("proDashboard")
    else:
        return redirect("userDashboard")

def userDashboard(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")
    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, "userDashboard.html", params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def userDashboardApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "cart_total": cart_total,
        "categories": serialized_categories
    })


def supportPage(request):
    try:
        username = request.session["username"]
    except:
        username = None
    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    request_submitted = False
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        description = request.POST.get("description")

        image1 = request.FILES["file_uploaded"]
        fs1 = FileSystemStorage()
        filename1 = fs1.save(image1.name, image1)
        file_url = fs1.url(filename1)

        category = request.POST.get("category")

        support_request = SupportRequest(
            name=name,
            email=email,
            subject=subject,
            description=description,
            image=file_url,
            category=category
        )
        support_request.save()
        request_submitted = True

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total,
        "request_submitted": request_submitted
    }
    return render(request, 'support.html', params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def supportPageApi(request):
    user = request.user

    cart_total = 0.00
    username = user.name
    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    request_submitted = False
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        description = request.POST.get("description")

        image1 = request.FILES["file_uploaded"]
        fs1 = FileSystemStorage()
        filename1 = fs1.save(image1.name, image1)
        file_url = fs1.url(filename1)

        category = request.POST.get("category")

        support_request = SupportRequest(
            name=name,
            email=email,
            subject=subject,
            description=description,
            image=file_url,
            category=category
        )
        support_request.save()
        request_submitted = True

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "categories": serialized_categories,
        "request_submitted": request_submitted,
        "cart_total": cart_total
    })

def buyerTerms(request):
    try:
        username = request.session["username"]
    except:
        username = None
    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'buyerTerms.html', params)

@api_view(["POST"])
def buyerTermsApi(request):
    user = request.user

    cart_total = 0.00
    if str(user) != "AnonymousUser":
        username = user.name
        userDB = UserDatabase.objects.get(username=username)
        buyer_id = userDB.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "categories": serialized_categories,
        "cart_total": cart_total
    })

def sellerTerms(request):
    try:
        username = request.session["username"]
    except:
        username = None
    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'sellerTerms.html', params)

@api_view(["POST"])
def sellerTermsApi(request):
    user = request.user

    cart_total = 0.00
    if str(user) != "AnonymousUser":
        username = user.name
        userDB = UserDatabase.objects.get(username=username)
        buyer_id = userDB.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "categories": serialized_categories,
        "cart_total": cart_total
    })

def refundPolicy(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'refund.html', params)

@api_view(["POST"])
def refundPolicyApi(request):
    user = request.user

    cart_total = 0.00
    if str(user) != "AnonymousUser":
        username = user.name
        userDB = UserDatabase.objects.get(username=username)
        buyer_id = userDB.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "categories": serialized_categories,
        "cart_total": cart_total
    })

def passwordReset(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'passwordReset.html', params)

def ordersPage(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    orders = Order.objects.filter(buyer_id=buyer_id)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total,
        "orders": orders
    }
    return render(request, 'ordersPage.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def ordersPageApi(request):
    user = request.user
    username = user.name

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    orders = Order.objects.filter(buyer_id=buyer_id)
    categories = Category.objects.all()

    serialized_orders = OrderSerializer(orders, many=True)
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "categories": serialized_categories,
        "orders": serialized_orders
    })

def subscriptionsPage(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'subscriptionsPage.html', params)

def downloadsPage(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)


    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'downloadsPage.html', params)

def addressPage(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'addressPage.html', params)

@api_view(["POST"])
def addressPageApi(request):
    user = request.user

    cart_total = 0.00
    if str(user) != "AnonymousUser":
        username = user.name
        userDB = UserDatabase.objects.get(username=username)
        buyer_id = userDB.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "categories": serialized_categories,
        "cart_total": cart_total
    })

def accountPage(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id

    try:
        buyerAddress = BuyerAddress.objects.get(user_id=user_id)
    except:
        categories = Category.objects.all()
        params = {
            "categories": categories,
            "cart_total": cart_total
        }
        return render(request, "accountPage.html", params)

    first_name = buyerAddress.first_name
    last_name = buyerAddress.last_name
    email = buyerAddress.email

    categories = Category.objects.all()
    params = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "categories": categories,
                "cart_total": cart_total
            }

    return render(request, 'accountPage.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def accountPageApi(request):
    user = request.user

    cart_total = 0.00

    username = user.name
    userDB = UserDatabase.objects.get(username=username)
    buyer_id = userDB.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    try:
        buyerAddress = BuyerAddress.objects.get(user_id=buyer_id)
    except:
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True)

        return Response({
            "categories": serialized_categories,
            "cart_total": cart_total
        })

    first_name = buyerAddress.first_name
    last_name = buyerAddress.last_name
    email = buyerAddress.email

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    return Response({
        "categories": serialized_categories,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "cart_total": cart_total
    })

def becomeSellerPage(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    if request.method == "POST":
        user = UserDatabase.objects.get(username=username)
        user.user_type = "MERCHANT"
        user.save()

        return redirect("proSettings")

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'becomeSellerPage.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def becomeSellerPageApi(request):
    user = request.user

    cart_total = 0.00

    if str(user) != "AnonymousUser":
        username = user.name
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "categories": serialized_categories,
        "cart_total": cart_total
    }
    return Response(params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def becomeSellerPageApi2(request):
    user = request.user

    cart_total = 0.00

    if str(user) != "AnonymousUser":
        username = user.name
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    if request.method == "POST":
        user = UserDatabase.objects.get(username=username)
        user.user_type = "MERCHANT"
        user.save()

        return redirect("proSettings")

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "categories": serialized_categories,
        "cart_total": cart_total
    }
    return Response(params)

def proDashboard(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id

    orders = Order.objects.filter(seller_id=user_id)

    num_orders = 0
    amount_orders = 0.00
    for order in orders:
        num_orders += 1
        try:
            amount_orders += float(order.price)
        except:
            amount_orders += 0.00

    products = Product.objects.filter(seller_id=user_id)

    num_products = 0
    amount_products = 0.00
    for product in products:
        num_products += 1
        try:
            amount_products += float(product.sale_price)
        except:
            amount_products += 0.00

    categories = Category.objects.all()
    params = {
        "num_orders": num_orders,
        "amount_orders": amount_orders,
        "num_products": num_products,
        "amount_products": amount_products,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request, 'proDashboard.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proDashboardApi(request):
    user = request.user

    cart_total = 0.00

    username = user.name
    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id

    orders = Order.objects.filter(seller_id=user_id)

    num_orders = 0
    amount_orders = 0.00
    for order in orders:
        num_orders += 1
        try:
            amount_orders += float(order.price)
        except:
            amount_orders += 0.00

    products = Product.objects.filter(seller_id=user_id)

    num_products = 0
    amount_products = 0.00
    for product in products:
        num_products += 1
        try:
            amount_products += float(product.sale_price)
        except:
            amount_products += 0.00

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "num_orders": num_orders,
        "amount_orders": amount_orders,
        "num_products": num_products,
        "amount_products": amount_products,
        "categories": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def proProducts(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id
    allProducts = Product.objects.filter(seller_id=user_id)

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    store = Store.objects.get(seller_id=user_id)
    is_member = True
    if store.membership_status == "inactive":
        is_member = False

    categories = Category.objects.all()
    params = {
        "products": products,
        "next_page": next_page,
        "prev_page": prev_page,
        "categories": categories,
        "cart_total": cart_total,
        "is_member": is_member
    }

    return render(request, 'proProducts.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proProductsApi(request):
    user = request.user

    cart_total = 0.00

    username = user.name
    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id
    allProducts = Product.objects.filter(seller_id=user_id)

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    store = Store.objects.get(seller_id=user_id)
    is_member = True
    if store.membership_status == "inactive":
        is_member = False

    serialized_products = ProductSerializer(products, many=True)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "products": serialized_products,
        "next_page": next_page,
        "prev_page": prev_page,
        "categories": serialized_categories,
        "cart_total": cart_total,
        "is_member": is_member
    }

    return Response(params)

def addProduct(request):

    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    product_saved = False

    if (request.method == "POST"):
        product_name = request.POST.get("product_name")
        product_description = request.POST.get("product_description")
        product_short_description = request.POST.get("product_short_description")
        category_name = request.POST.get("categoryName")

        category = Category.objects.get(name=category_name)
        category_id = category.id

        image1 = request.FILES["image1_file"]
        fs1 = FileSystemStorage()
        filename1 = fs1.save(image1.name, image1)
        image1_url = fs1.url(filename1)

        image2 = request.FILES["image2_file"]
        fs2 = FileSystemStorage()
        filename2 = fs2.save(image2.name, image2)
        image2_url = fs2.url(filename2)

        image3 = request.FILES["image3_file"]
        fs3 = FileSystemStorage()
        filename3 = fs3.save(image3.name, image3)
        image3_url = fs3.url(filename3)

        product_type = request.POST.get("product-type")
        regular_price = request.POST.get("regular-price")
        sale_price = request.POST.get("sale-price")
        tax_status = request.POST.get("tax-status")
        tax_class = request.POST.get("tax-class")
        stock_status = request.POST.get("stock-status")

        seller = request.session["username"]
        user = UserDatabase.objects.get(username=seller)
        seller_id = user.id

        product = Product(
            name=product_name,
            description=product_description,
            short_description=product_short_description,
            category_id= category_id,
            image1=image1_url,
            image2=image2_url,
            image3=image3_url,
            type=product_type,
            price=regular_price,
            sale_price=sale_price,
            tax_status=tax_status,
            tax_class=tax_class,
            stock_status=stock_status,
            seller_id=seller_id
        )
        product.save()
        product_saved = True

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "saved": product_saved,
        "cart_total": cart_total
    }
    return render(request, 'addProduct.html', params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def addProductApi(request):
    user = request.user

    cart_total = 0.00

    username = user.name
    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    product_saved = False

    product_name = request.POST.get("product_name")
    product_description = request.POST.get("product_description")
    product_short_description = request.POST.get("product_short_description")
    category_name = request.POST.get("categoryName")

    category = Category.objects.get(name=category_name)
    category_id = category.id

    image1 = request.FILES["image1_file"]
    fs1 = FileSystemStorage()
    filename1 = fs1.save(image1.name, image1)
    image1_url = fs1.url(filename1)

    image2 = request.FILES["image2_file"]
    fs2 = FileSystemStorage()
    filename2 = fs2.save(image2.name, image2)
    image2_url = fs2.url(filename2)

    image3 = request.FILES["image3_file"]
    fs3 = FileSystemStorage()
    filename3 = fs3.save(image3.name, image3)
    image3_url = fs3.url(filename3)

    product_type = request.POST.get("product-type")
    regular_price = request.POST.get("regular-price")
    sale_price = request.POST.get("sale-price")
    tax_status = request.POST.get("tax-status")
    tax_class = request.POST.get("tax-class")
    stock_status = request.POST.get("stock-status")

    seller = request.session["username"]
    user = UserDatabase.objects.get(username=seller)
    seller_id = user.id

    product = Product(
        name=product_name,
        description=product_description,
        short_description=product_short_description,
        category_id= category_id,
        image1=image1_url,
        image2=image2_url,
        image3=image3_url,
        type=product_type,
        price=regular_price,
        sale_price=sale_price,
        tax_status=tax_status,
        tax_class=tax_class,
        stock_status=stock_status,
        seller_id=seller_id
    )
    product.save()
    product_saved = True

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "categories": serialized_categories,
        "saved": product_saved,
        "cart_total": cart_total
    }
    return Response(params)

def proUpdateProduct(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    product_modified = False
    if request.method == "POST":

        product_id = request.POST.get("product_id")

        product_name = request.POST.get("product_name")
        product_description = request.POST.get("product_description")
        product_short_description = request.POST.get("product_short_description")
        category_name = request.POST.get("categoryName")

        category = Category.objects.get(name=category_name)
        category_id = category.id

        try:
            image1 = request.FILES["image1_file"]
            fs1 = FileSystemStorage()
            filename1 = fs1.save(image1.name, image1)
            image1_url = fs1.url(filename1)
        except:
            image1_url = ""

        try:
            image2 = request.FILES["image2_file"]
            fs2 = FileSystemStorage()
            filename2 = fs2.save(image2.name, image2)
            image2_url = fs2.url(filename2)
        except:
            image2_url = ""

        try:
            image3 = request.FILES["image3_file"]
            fs3 = FileSystemStorage()
            filename3 = fs3.save(image3.name, image3)
            image3_url = fs3.url(filename3)
        except:
            image3_url = ""

        product_type = request.POST.get("product-type")
        regular_price = request.POST.get("regular-price")
        sale_price = request.POST.get("sale-price")
        tax_status = request.POST.get("tax-status")
        tax_class = request.POST.get("tax-class")
        stock_status = request.POST.get("stock-status")

        seller = request.session["username"]
        user = UserDatabase.objects.get(username=seller)
        seller_id = user.id

        product = Product.objects.get(id=product_id)

        if product_name != "":
            product.name = product_name

        if product_description != "":
            product.description = product_description

        if product_short_description != "":
            product.short_description = product_short_description

        if category_id != "":
            product.category_id = category_id

        if image1_url != "":
            product.image1 = image1_url

        if image2_url != "":
            product.image2 = image2

        if image3_url != "":
            product.image3 = image3_url

        if product_type != "":
            product.type = product_type

        if regular_price != "":
            product.price = regular_price

        if sale_price != "":
            product.sale_price = sale_price

        if tax_status != "":
            product.tax_status = tax_status

        if tax_class != "":
            product.tax_class = tax_class

        if stock_status != "":
            product.stock_status = stock_status

        product.save()
        product_modified = True

        return redirect("proProducts")

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id

    product_id = request.GET.get("product_id")
    product = Product.objects.get(id=product_id, seller_id=seller_id)

    categories = Category.objects.all()

    params = {
                "seller_id": seller_id,
                "product": product,
                "product_modified": product_modified,
                "categories": categories,
                "cart_items": cart_items
            }

    return render(request, "proUpdateProduct.html", params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proUpdateProductPost(request):
    user = request.user

    cart_total = 0.00

    username = user.name
    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    product_modified = False

    product_id = request.POST.get("product_id")

    product_name = request.POST.get("product_name")
    product_description = request.POST.get("product_description")
    product_short_description = request.POST.get("product_short_description")
    category_name = request.POST.get("categoryName")

    category = Category.objects.get(name=category_name)
    category_id = category.id

    try:
        image1 = request.FILES["image1_file"]
        fs1 = FileSystemStorage()
        filename1 = fs1.save(image1.name, image1)
        image1_url = fs1.url(filename1)
    except:
        image1_url = ""

    try:
        image2 = request.FILES["image2_file"]
        fs2 = FileSystemStorage()
        filename2 = fs2.save(image2.name, image2)
        image2_url = fs2.url(filename2)
    except:
        image2_url = ""

    try:
        image3 = request.FILES["image3_file"]
        fs3 = FileSystemStorage()
        filename3 = fs3.save(image3.name, image3)
        image3_url = fs3.url(filename3)
    except:
        image3_url = ""

    product_type = request.POST.get("product-type")
    regular_price = request.POST.get("regular-price")
    sale_price = request.POST.get("sale-price")
    tax_status = request.POST.get("tax-status")
    tax_class = request.POST.get("tax-class")
    stock_status = request.POST.get("stock-status")

    seller = request.session["username"]
    user = UserDatabase.objects.get(username=seller)
    seller_id = user.id

    product = Product.objects.get(id=product_id)

    if product_name != "":
        product.name = product_name

    if product_description != "":
        product.description = product_description

    if product_short_description != "":
        product.short_description = product_short_description

    if category_id != "":
        product.category_id = category_id

    if image1_url != "":
        product.image1 = image1_url

    if image2_url != "":
        product.image2 = image2

    if image3_url != "":
        product.image3 = image3_url

    if product_type != "":
        product.type = product_type

    if regular_price != "":
        product.price = regular_price

    if sale_price != "":
        product.sale_price = sale_price

    if tax_status != "":
        product.tax_status = tax_status

    if tax_class != "":
        product.tax_class = tax_class

    if stock_status != "":
        product.stock_status = stock_status

    product.save()
    product_modified = True

    params = {
                "product_modified": product_modified
            }

    return Response(params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proUpdateProductGet(request):
    user = request.user

    cart_total = 0.00

    username = user.name
    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id

    product_id = request.GET.get("product_id")
    product = Product.objects.get(id=product_id, seller_id=seller_id)
    serialized_product = ProductSerializer(product)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    params = {
                "seller_id": seller_id,
                "product": serialized_product,
                "categories": serialized_categories,
                "cart_items": cart_items
            }

    return Response(params)

def proOrders(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    products = Order.objects.filter(seller_id=buyer_id)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total,
        "products": products
    }
    return render(request, 'proOrders.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proOrdersApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    products = Order.objects.filter(seller_id=buyer_id)
    serialized_orders = OrderSerializer(products, many=True)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    params = {
        "categories": serialized_categories,
        "cart_total": cart_total,
        "products": serialized_orders
    }
    return Response(params)

def proSettings(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    settings_updated = False

    if request.method == "POST":
        store_name = request.POST.get("store-name")
        store_description = request.POST.get("store-description")
        seller_info = request.POST.get("seller-info")
        store_url = request.POST.get("store-url")
        store_phone = request.POST.get("store-phone")
        store_country = request.POST.get("store-country")
        store_address = request.POST.get("store-address")
        store_city = request.POST.get("city-town")
        store_state = request.POST.get("store-state")
        store_post_code = request.POST.get("postal-code")

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id

        try:
            prevStore = Store.objects.get(seller_id=seller_id)
        except:
            prevStore = None

        if prevStore is None:
            store = Store(
                name=store_name,
                description=store_description,
                seller_info=seller_info,
                url=store_url,
                phone=store_phone,
                country=store_country,
                address=store_address,
                city=store_city,
                state=store_state,
                postal_code=store_post_code,
                seller_id=seller_id
            )
            store.save()
        else:
            if store_name != "":
                prevStore.name = store_name

            if store_description != "":
                prevStore.description = store_description

            if seller_info != "":
                prevStore.seller_info = seller_info

            if store_url != "":
                prevStore.url = store_url

            if store_phone != "":
                prevStore.phone = store_phone

            if store_country != "":
                prevStore.country = store_country

            if store_address != "":
                prevStore.address = store_address

            if store_city != "":
                prevStore.city = store_city

            if store_state != "":
                prevStore.state = store_state

            if store_post_code != "":
                prevStore.postal_code = store_post_code

            prevStore.save()

        settings_updated = True

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    try:
        store = Store.objects.get(seller_id=seller_id)
    except:
        store = None

    categories = Category.objects.all()
    states = StoreState.objects.all()
    params = {
        "states": states,
        "settings": settings_updated,
        "store": store,
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'proSettings.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proSettingsApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    settings_updated = False

    if request.method == "POST":
        store_name = request.POST.get("store-name")
        store_description = request.POST.get("store-description")
        seller_info = request.POST.get("seller-info")
        store_url = request.POST.get("store-url")
        store_phone = request.POST.get("store-phone")
        store_country = request.POST.get("store-country")
        store_address = request.POST.get("store-address")
        store_city = request.POST.get("city-town")
        store_state = request.POST.get("store-state")
        store_post_code = request.POST.get("postal-code")

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id

        try:
            prevStore = Store.objects.get(seller_id=seller_id)
        except:
            prevStore = None

        if prevStore is None:
            store = Store(
                name=store_name,
                description=store_description,
                seller_info=seller_info,
                url=store_url,
                phone=store_phone,
                country=store_country,
                address=store_address,
                city=store_city,
                state=store_state,
                postal_code=store_post_code,
                seller_id=seller_id
            )
            store.save()
        else:
            if store_name != "":
                prevStore.name = store_name

            if store_description != "":
                prevStore.description = store_description

            if seller_info != "":
                prevStore.seller_info = seller_info

            if store_url != "":
                prevStore.url = store_url

            if store_phone != "":
                prevStore.phone = store_phone

            if store_country != "":
                prevStore.country = store_country

            if store_address != "":
                prevStore.address = store_address

            if store_city != "":
                prevStore.city = store_city

            if store_state != "":
                prevStore.state = store_state

            if store_post_code != "":
                prevStore.postal_code = store_post_code

            prevStore.save()

        settings_updated = True

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    try:
        store = Store.objects.get(seller_id=seller_id)
    except:
        store = None

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    states = StoreState.objects.all()
    serialized_states = StoreStateSerializer(states, many=True)
    params = {
        "states": serialized_states,
        "settings": settings_updated,
        "store": store,
        "categories": serialized_categories,
        "cart_total": cart_total
    }
    return Response(params)

def proPayments(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    paymentStatus = False

    seller = UserDatabase.objects.get(username=username)
    seller_id = seller.id

    if request.method == "POST":
        paypal_address = request.POST.get("paypal_address")
        bank_account_name = request.POST.get("bank_account_name")
        bank_account_number = request.POST.get("bank_account_number")
        bank_name = request.POST.get("bank_name")
        bank_routing_number = request.POST.get("bank_routing_number")
        bank_IBAN = request.POST.get("bank_IBAN")
        bank_BIC_SWIFT = request.POST.get("bank_BIC_SWIFT")

        try:
            prevPayment = SellerPaymentDetail.objects.get(seller_id=seller_id)
        except:
            prevPayment = None

        if prevPayment is None:
            payment = SellerPaymentDetail(
                seller_id = seller_id,
                paypal_address=paypal_address,
                bank_account_name=bank_account_name,
                bank_routing_number=bank_routing_number,
                bank_account_number=bank_account_number,
                bank_name=bank_name,
                bank_IBAN=bank_IBAN,
                bank_BIC_SWIFT=bank_BIC_SWIFT
            )
            payment.save()
        else:
            if paypal_address != "":
                prevPayment.paypal_address = paypal_address
            if bank_account_name != "":
                prevPayment.bank_account_name = bank_account_name
            if bank_account_number != "":
                prevPayment.bank_account_number = bank_account_number
            if bank_routing_number != "":
                prevPayment.bank_routing_number = bank_routing_number
            if bank_name != "":
                prevPayment.bank_name = bank_name
            if bank_IBAN != "":
                prevPayment.bank_IBAN = bank_IBAN
            if bank_BIC_SWIFT != "":
                prevPayment.bank_BIC_SWIFT = bank_BIC_SWIFT

            prevPayment.save()

        paymentStatus = True

    try:
        payment = SellerPaymentDetail.objects.get(seller_id=seller_id)
    except:
        payment = None

    categories = Category.objects.all()
    params = {
        "paymentStatus": paymentStatus,
        "payment": payment,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request, 'proPayments.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proPaymentsApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    paymentStatus = False

    seller = UserDatabase.objects.get(username=username)
    seller_id = seller.id

    if request.method == "POST":
        paypal_address = request.POST.get("paypal_address")
        bank_account_name = request.POST.get("bank_account_name")
        bank_account_number = request.POST.get("bank_account_number")
        bank_name = request.POST.get("bank_name")
        bank_routing_number = request.POST.get("bank_routing_number")
        bank_IBAN = request.POST.get("bank_IBAN")
        bank_BIC_SWIFT = request.POST.get("bank_BIC_SWIFT")

        try:
            prevPayment = SellerPaymentDetail.objects.get(seller_id=seller_id)
        except:
            prevPayment = None

        if prevPayment is None:
            payment = SellerPaymentDetail(
                seller_id = seller_id,
                paypal_address=paypal_address,
                bank_account_name=bank_account_name,
                bank_routing_number=bank_routing_number,
                bank_account_number=bank_account_number,
                bank_name=bank_name,
                bank_IBAN=bank_IBAN,
                bank_BIC_SWIFT=bank_BIC_SWIFT
            )
            payment.save()
        else:
            if paypal_address != "":
                prevPayment.paypal_address = paypal_address
            if bank_account_name != "":
                prevPayment.bank_account_name = bank_account_name
            if bank_account_number != "":
                prevPayment.bank_account_number = bank_account_number
            if bank_routing_number != "":
                prevPayment.bank_routing_number = bank_routing_number
            if bank_name != "":
                prevPayment.bank_name = bank_name
            if bank_IBAN != "":
                prevPayment.bank_IBAN = bank_IBAN
            if bank_BIC_SWIFT != "":
                prevPayment.bank_BIC_SWIFT = bank_BIC_SWIFT

            prevPayment.save()

        paymentStatus = True

    try:
        payment = SellerPaymentDetail.objects.get(seller_id=seller_id)
        serialized_payments = SellerPaymentDetailSerializer(payment)
    except:
        payment = None
        serialized_payments = None

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "paymentStatus": paymentStatus,
        "payment": serialized_payments,
        "categories": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def proBranding(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    images_uploaded = False

    if request.method == "POST":
        fs = FileSystemStorage()

        store_banner = request.FILES["store_banner"]
        store_banner_name = fs.save(store_banner.name, store_banner)
        store_banner_url = fs.url(store_banner_name)

        store_icon = request.FILES["store_icon"]
        store_icon_name = fs.save(store_icon.name, store_icon)
        store_icon_url = fs.url(store_icon_name)

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id

        store = Store.objects.get(seller_id=seller_id)

        store.store_banner = store_banner_url
        store.store_icon = store_icon_url

        store.save()

        images_uploaded = True

    categories = Category.objects.all()
    params = {
        "images_uploaded": images_uploaded,
        "categories": categories,
        "cart_items": cart_items
    }
    return render(request, 'proBranding.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proBrandingApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    images_uploaded = False

    if request.method == "POST":
        fs = FileSystemStorage()

        store_banner = request.FILES["store_banner"]
        store_banner_name = fs.save(store_banner.name, store_banner)
        store_banner_url = fs.url(store_banner_name)

        store_icon = request.FILES["store_icon"]
        store_icon_name = fs.save(store_icon.name, store_icon)
        store_icon_url = fs.url(store_icon_name)

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id

        store = Store.objects.get(seller_id=seller_id)

        store.store_banner = store_banner_url
        store.store_icon = store_icon_url

        store.save()

        images_uploaded = True

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "images_uploaded": images_uploaded,
        "categories": serialized_categories,
        "cart_total": cart_total
    }
    return Response(params)

def proShipping(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    shipping_enabled = False

    if request.method == "POST":
        shipping_type = request.POST.get("shipping-type")
        national_shipping_fee = request.POST.get("national-shipping-fee")
        national_free_shipping_fee = request.POST.get("national-flat-shipping-fee")
        national_free_shipping_enabled = request.POST.get("free-national-shipping-fee")
        disable_national_shipping = request.POST.get("disable-national-shipping-fee")
        international_shipping_fee = request.POST.get("international-shipping-fee")
        international_free_shipping_fee = request.POST.get("international-flat-shipping-fee")
        international_free_shipping_enabled = request.POST.get("free-international-shipping-fee")
        disable_international_shipping = request.POST.get("disable-international-shipping-fee")
        product_handling_fee = request.POST.get("product-handling-fee")
        shipping_address_type = request.POST.get("shipping-address-type")

        shipping_country = ""
        shipping_address = ""
        shipping_city = ""
        shipping_state = ""
        shipping_postcode = ""

        if shipping_address_type == "Other":
            shipping_country = request.POST.get("shipping-country")
            shipping_address = request.POST.get("shipping-address")
            shipping_city = request.POST.get("city-town")
            shipping_state = request.POST.get("state-county")
            shipping_postcode = request.POST.get("postcode")
        else:
            username = request.session["username"]
            user = UserDatabase.objects.get(username=username)
            user_id = user.id
            store = Store.objects.get(seller_id=user_id)

            shipping_country = store.country
            shipping_address = store.address
            shipping_city = store.city
            shipping_state = store.state
            shipping_postcode = store.postal_code

        try:
            prevShipping = Shipping.objects.get(seller_id=user_id)
        except:
            prevShipping = None

        if prevShipping is None:

            shipping = Shipping(
                seller_id=user_id,
                shipping_type=shipping_type,
                national_shipping_fee=national_shipping_fee,
                national_free_shipping_fee=national_free_shipping_fee,
                national_free_shipping_enabled=national_free_shipping_enabled,
                disable_national_shipping=disable_national_shipping,
                international_shipping_fee=international_shipping_fee,
                international_free_shipping_fee=international_free_shipping_fee,
                international_free_shipping_enabled=international_free_shipping_enabled,
                disable_international_shipping=disable_international_shipping,
                product_handling_fee=product_handling_fee,
                shipping_country=shipping_country,
                shipping_address=shipping_address,
                shipping_city=shipping_city,
                shipping_state=shipping_state,
                shipping_postcode=shipping_postcode
            )
            shipping.save()
        else:
            if shipping_type != "":
                prevShipping.shipping_type = shipping_type

            if national_shipping_fee != "":
                prevShipping.national_shipping_fee = national_shipping_fee

            if national_free_shipping_fee != "":
                prevShipping.national_free_shipping_fee = national_free_shipping_fee

            if international_shipping_fee != "":
                prevShipping.international_shipping_fee = international_shipping_fee

            if international_free_shipping_fee != "":
                prevShipping.international_free_shipping_fee = international_free_shipping_fee

            if product_handling_fee != "":
                prevShipping.product_handling_fee = product_handling_fee

            if shipping_country != "":
                prevShipping.shipping_country = shipping_country

            if shipping_address != "":
                prevShipping.shipping_address = shipping_address

            if shipping_city != "":
                prevShipping.shipping_city = shipping_city

            if shipping_state != "":
                prevShipping.shipping_state = shipping_state

            if shipping_postcode != "":
                prevShipping.shipping_postcode = shipping_postcode

            prevShipping.save()

        shipping_enabled = True

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id

    try:
        shipping = Shipping.objects.get(seller_id=seller_id)
    except:
        shipping = None

    categories = Category.objects.all()
    params = {
        "shipping_enabled": shipping_enabled,
        "shipping": shipping,
        "category": categories,
        "cart_total": cart_total
    }

    return render(request, 'proShipping.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proShippingApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    shipping_enabled = False

    if request.method == "POST":
        shipping_type = request.POST.get("shipping-type")
        national_shipping_fee = request.POST.get("national-shipping-fee")
        national_free_shipping_fee = request.POST.get("national-flat-shipping-fee")
        national_free_shipping_enabled = request.POST.get("free-national-shipping-fee")
        disable_national_shipping = request.POST.get("disable-national-shipping-fee")
        international_shipping_fee = request.POST.get("international-shipping-fee")
        international_free_shipping_fee = request.POST.get("international-flat-shipping-fee")
        international_free_shipping_enabled = request.POST.get("free-international-shipping-fee")
        disable_international_shipping = request.POST.get("disable-international-shipping-fee")
        product_handling_fee = request.POST.get("product-handling-fee")
        shipping_address_type = request.POST.get("shipping-address-type")

        shipping_country = ""
        shipping_address = ""
        shipping_city = ""
        shipping_state = ""
        shipping_postcode = ""

        if shipping_address_type == "Other":
            shipping_country = request.POST.get("shipping-country")
            shipping_address = request.POST.get("shipping-address")
            shipping_city = request.POST.get("city-town")
            shipping_state = request.POST.get("state-county")
            shipping_postcode = request.POST.get("postcode")
        else:
            username = request.session["username"]
            user = UserDatabase.objects.get(username=username)
            user_id = user.id
            store = Store.objects.get(seller_id=user_id)

            shipping_country = store.country
            shipping_address = store.address
            shipping_city = store.city
            shipping_state = store.state
            shipping_postcode = store.postal_code

        try:
            prevShipping = Shipping.objects.get(seller_id=user_id)
        except:
            prevShipping = None

        if prevShipping is None:

            shipping = Shipping(
                seller_id=user_id,
                shipping_type=shipping_type,
                national_shipping_fee=national_shipping_fee,
                national_free_shipping_fee=national_free_shipping_fee,
                national_free_shipping_enabled=national_free_shipping_enabled,
                disable_national_shipping=disable_national_shipping,
                international_shipping_fee=international_shipping_fee,
                international_free_shipping_fee=international_free_shipping_fee,
                international_free_shipping_enabled=international_free_shipping_enabled,
                disable_international_shipping=disable_international_shipping,
                product_handling_fee=product_handling_fee,
                shipping_country=shipping_country,
                shipping_address=shipping_address,
                shipping_city=shipping_city,
                shipping_state=shipping_state,
                shipping_postcode=shipping_postcode
            )
            shipping.save()
        else:
            if shipping_type != "":
                prevShipping.shipping_type = shipping_type

            if national_shipping_fee != "":
                prevShipping.national_shipping_fee = national_shipping_fee

            if national_free_shipping_fee != "":
                prevShipping.national_free_shipping_fee = national_free_shipping_fee

            if international_shipping_fee != "":
                prevShipping.international_shipping_fee = international_shipping_fee

            if international_free_shipping_fee != "":
                prevShipping.international_free_shipping_fee = international_free_shipping_fee

            if product_handling_fee != "":
                prevShipping.product_handling_fee = product_handling_fee

            if shipping_country != "":
                prevShipping.shipping_country = shipping_country

            if shipping_address != "":
                prevShipping.shipping_address = shipping_address

            if shipping_city != "":
                prevShipping.shipping_city = shipping_city

            if shipping_state != "":
                prevShipping.shipping_state = shipping_state

            if shipping_postcode != "":
                prevShipping.shipping_postcode = shipping_postcode

            prevShipping.save()

        shipping_enabled = True

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id

    try:
        shipping = Shipping.objects.get(seller_id=seller_id)
        serialized_shipping = ShippingSerializer(shipping)
    except:
        shipping = None
        serialized_shipping = None

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "shipping_enabled": shipping_enabled,
        "shipping": serialized_shipping,
        "category": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def proSocial(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    social_handles_updated = False

    if request.method == 'POST':
        twitter_username = request.POST.get("twitter-username")
        instagram_username = request.POST.get("instagram-username")
        facebook_url = request.POST.get("facebook-url")
        linkedin_url = request.POST.get("linkedin-url")
        youtube_url = request.POST.get("youtube-url")
        pinterest_url = request.POST.get("pinterest-url")
        snapchat_username = request.POST.get("snapchat-username")
        telegram_username = request.POST.get("telegram-username")

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id
        store = Store.objects.get(seller_id=seller_id)

        store.twitter_username = twitter_username
        store.instagram_username = instagram_username
        store.facebook_url = facebook_url
        store.linkedin_url = linkedin_url
        store.youtube_url = youtube_url
        store.pinterest_url = pinterest_url
        store.snapchat_username = snapchat_username
        store.telegram_username = telegram_username

        store.save()

        social_handles_updated = True

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    try:
        store = Store.objects.get(seller_id=seller_id)
    except:
        store = None

    categories = Category.objects.all()
    params = {
        "social": social_handles_updated,
        "store": store,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request,"proSocial.html", params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proSocialApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    social_handles_updated = False

    if request.method == 'POST':
        twitter_username = request.POST.get("twitter-username")
        instagram_username = request.POST.get("instagram-username")
        facebook_url = request.POST.get("facebook-url")
        linkedin_url = request.POST.get("linkedin-url")
        youtube_url = request.POST.get("youtube-url")
        pinterest_url = request.POST.get("pinterest-url")
        snapchat_username = request.POST.get("snapchat-username")
        telegram_username = request.POST.get("telegram-username")

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id
        store = Store.objects.get(seller_id=seller_id)

        store.twitter_username = twitter_username
        store.instagram_username = instagram_username
        store.facebook_url = facebook_url
        store.linkedin_url = linkedin_url
        store.youtube_url = youtube_url
        store.pinterest_url = pinterest_url
        store.snapchat_username = snapchat_username
        store.telegram_username = telegram_username

        store.save()

        social_handles_updated = True

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    try:
        store = Store.objects.get(seller_id=seller_id)
        serialized_store = StoreSerializer(store)
    except:
        store = None
        serialized_store = None

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "social": social_handles_updated,
        "store": serialized_store,
        "categories": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def proPolicy(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    policy_updated = False

    if request.method == "POST":
        terms_and_conditions = request.POST.get("terms-and-conditions")

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id
        store = Store.objects.get(seller_id=seller_id)

        store.terms_and_conditions = terms_and_conditions
        store.save()

        policy_updated = True

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    try:
        store = Store.objects.get(seller_id=seller_id)
    except:
        store = None

    categories = Category.objects.all()
    params = {
        "policy": policy_updated,
        "store": store,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request,"proPolicy.html", params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proPolicyApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    policy_updated = False

    if request.method == "POST":
        terms_and_conditions = request.POST.get("terms-and-conditions")

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id
        store = Store.objects.get(seller_id=seller_id)

        store.terms_and_conditions = terms_and_conditions
        store.save()

        policy_updated = True

    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    try:
        store = Store.objects.get(seller_id=seller_id)
        serialized_store = StoreSerializer(store)
    except:
        store = None
        serialized_store = None

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "policy": policy_updated,
        "store": serialized_store,
        "categories": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def proMembership(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    username = request.session["username"]
    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    print("SELLER ID")
    print(seller_id)
    try:
        store = Store.objects.get(seller_id=seller_id)
    except:
        store = None

    products = Product.objects.filter(seller_id=seller_id)
    product_count = 0
    for product in products:
        product_count += 1

    categories = Category.objects.all()

    membership_prices = MembershipPrice.objects.get()

    if store is not None:
        if store.membership_type == "ANNUAL SELLER MEMBERSHIP":
            if (date.today() - store.membership_start_date) > timedelta(365):
                store.membership_status = "inactive"
            else:
                store.membership_status = "active"
        elif store.membership_type == "MONTHLY SELLER MEMBERSHIP":
            if (date.today() - store.membership_start_date) > timedelta(30):
                store.membership_status = "inactive"
            else:
                store.membership_status = "active"
        else:
            store.membership_status = "inactive"

        store.save()

        params = {
            "membership_type": store.membership_type,
            "membership_status": store.membership_status,
            "start_date": store.membership_start_date,
            "product_count": product_count,
            "categories": categories,
            "cart_total": cart_total,
            "membership_prices": membership_prices
        }
    else:
        params = {
            "product_count": product_count,
            "categories": categories,
            "cart_total": cart_total,
            "membership_prices": membership_prices
        }

    return render(request,"proMembership.html", params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proMembershipApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    username = request.session["username"]
    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    print("SELLER ID")
    print(seller_id)
    try:
        store = Store.objects.get(seller_id=seller_id)
    except:
        store = None

    products = Product.objects.filter(seller_id=seller_id)
    product_count = 0
    for product in products:
        product_count += 1

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)

    membership_prices = MembershipPrice.objects.get()
    serialized_membership_prices = MembershipPriceSerializer(membership_prices)

    if store is not None:
        if store.membership_type == "ANNUAL SELLER MEMBERSHIP":
            if (date.today() - store.membership_start_date) > timedelta(365):
                store.membership_status = "inactive"
            else:
                store.membership_status = "active"
        elif store.membership_type == "MONTHLY SELLER MEMBERSHIP":
            if (date.today() - store.membership_start_date) > timedelta(30):
                store.membership_status = "inactive"
            else:
                store.membership_status = "active"
        else:
            store.membership_status = "inactive"

        store.save()

        serialized_store = StoreSerializer(store)

        params = {
            "membership_type": serialized_store.membership_type,
            "membership_status": serialized_store.membership_status,
            "start_date": serialized_store.membership_start_date,
            "product_count": product_count,
            "categories": serialized_categories,
            "cart_total": cart_total,
            "membership_prices": serialized_membership_prices
        }
    else:
        params = {
            "product_count": product_count,
            "categories": serialized_categories,
            "cart_total": cart_total,
            "membership_prices": serialized_membership_prices
        }

    return Response(params)

def proRatings(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request,"proRatings.html", params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proRatingsApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "categories": serialized_categories,
        "cart_total": cart_total
    }
    return Response(params)

def proRefunds(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    orders = Order.objects.filter(seller_id=buyer_id)

    refunds = []

    for order in orders:
        if order.refund_status != "":
            refunds.append(order)

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total,
        "orders": refunds
    }
    return render(request,"proRefunds.html", params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proRefundsApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    orders = Order.objects.filter(seller_id=buyer_id)
    serialized_orders = OrderSerializer(orders, many=True)

    refunds = []

    for order in serialized_orders:
        if order.refund_status != "":
            refunds.append(order)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "categories": serialized_categories,
        "cart_total": cart_total,
        "orders": refunds
    }
    return Response(params)

def proCoupons(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id
    coupons = Coupon.objects.filter(seller_id=user_id)

    categories = Category.objects.all()
    params = {
                "coupons": coupons,
                "categories": categories,
                "cart_total": cart_total
            }

    return render(request,"proCoupons.html", params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proCouponsApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id
    coupons = Coupon.objects.filter(seller_id=user_id)
    serialized_coupons = CouponSerializer(coupons, many=True)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
                "coupons": serialized_coupons,
                "categories": serialized_categories,
                "cart_total": cart_total
            }

    return Response(params)

def proAddCoupon(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    coupon_added = False

    if request.method == "POST":
        coupon_code = request.POST.get("coupon-code")
        coupon_description = request.POST.get("coupon-description")
        discount_type = request.POST.get("discount-type")

        apply_to_all_products_boolean = False
        apply_to_all_products = request.POST.get("apply-to-all-products")
        if apply_to_all_products == "on":
            apply_to_all_products_boolean = True
        else:
            apply_to_all_products_boolean = False

        coupon_amount = request.POST.get("coupon-amount")

        allow_free_shipping_boolean = False
        allow_free_shipping = request.POST.get("allow-free-shipping")
        if allow_free_shipping == "on":
            allow_free_shipping_boolean = True
        else:
            allow_free_shipping_boolean = False

        coupon_expiry_date = request.POST.get("coupon-expiry-date")

        minimum_spend = request.POST.get("minimum-spend")

        maximum_spend = request.POST.get("maximum-spend")

        individual_use_only_formatted = False
        individual_use_only = request.POST.get("individual-use-only")
        if individual_use_only == "on":
            individual_use_only_formatted = True

        exclude_sale_items_formatted = False
        exclude_sale_items = request.POST.get("exclude-sale-items")
        if exclude_sale_items == "on":
            exclude_sale_items_formatted = True

        try:
            day = int(coupon_expiry_date[0:2])
            month = int(coupon_expiry_date[3:5])
            year = int(coupon_expiry_date[6:])
            coupon_expiry_date_formatted = date(year, month, day)
        except:
            coupon_expiry_date_formatted = date.today()

        email_restrictions = request.POST.get("email-restrictions")

        usage_limit_per_coupon = request.POST.get("usage-limit-per-coupon")
        if usage_limit_per_coupon == "":
            usage_limit_per_coupon_formatted = 1
        else:
            usage_limit_per_coupon_formatted = int(usage_limit_per_coupon)

        usage_limit_per_item = request.POST.get("usage-limit-per-item")
        if usage_limit_per_item == "":
            usage_limit_per_item_formatted = 1
        else:
            usage_limit_per_item_formatted = int(usage_limit_per_item)

        usage_limit_per_user = request.POST.get("usage-limit-per-user")
        if usage_limit_per_user == "":
            usage_limit_per_user_formatted = 1
        else:
            usage_limit_per_user_formatted = int(usage_limit_per_user)

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id

        try:
            prevCoupon = Coupon.objects.get(seller_id=seller_id)
        except:
            prevCoupon = None

        if prevCoupon is None:
            coupon = Coupon(
                seller_id=seller_id,
                code=coupon_code,
                description=coupon_description,
                discount_type=discount_type,
                apply_to_all_products=apply_to_all_products_boolean,
                coupon_amount=coupon_amount,
                allow_free_shipping=allow_free_shipping_boolean,
                coupon_expiry=coupon_expiry_date_formatted,
                minimum_spend=minimum_spend,
                maximum_spend=maximum_spend,
                individual_use_only=individual_use_only_formatted,
                exclude_sale_item=exclude_sale_items_formatted,
                restricted_emails=email_restrictions,
                usage_limit_per_coupon=usage_limit_per_coupon_formatted,
                usage_limit_item=usage_limit_per_item_formatted,
                usage_limit_per_user=usage_limit_per_user_formatted
            )
            coupon.save()
        else:
            if coupon_code != "":
                prevCoupon.code = coupon_code

            if coupon_description != "":
                prevCoupon.description = coupon_description

            if discount_type != "":
                prevCoupon.discount_type = discount_type

            prevCoupon.apply_to_all_products = apply_to_all_products_boolean

            if coupon_amount != "":
                prevCoupon.coupon_amount = coupon_amount

            prevCoupon.allow_free_shipping = allow_free_shipping_boolean

            prevCoupon.coupon_expiry= coupon_expiry_date_formatted

            prevCoupon.minimum_spend = minimum_spend

            prevCoupon.maximum_spend = maximum_spend

            prevCoupon.individual_use_only = individual_use_only_formatted

            prevCoupon.exclude_sale_item = exclude_sale_items_formatted

            prevCoupon.restricted_emails = email_restrictions

            prevCoupon.usage_limit_per_coupon = usage_limit_per_coupon_formatted

            prevCoupon.usage_limit_item = usage_limit_per_item_formatted

            prevCoupon.usage_limit_per_user = usage_limit_per_user_formatted

            prevCoupon.save()

        coupon_added = True
    try:
        coupon_id = request.GET.get("coupon_id")
        coupon = Coupon.objects.get(id=coupon_id)
    except:
        coupon = None

    categories = Category.objects.all()
    params = {
                "coupon_added": coupon_added,
                "coupon": coupon,
                "category": categories,
                "cart_total": cart_total
            }

    return render(request, 'addCoupon.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proAddCouponApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    coupon_added = False

    if request.method == "POST":
        coupon_code = request.POST.get("coupon-code")
        coupon_description = request.POST.get("coupon-description")
        discount_type = request.POST.get("discount-type")

        apply_to_all_products_boolean = False
        apply_to_all_products = request.POST.get("apply-to-all-products")
        if apply_to_all_products == "on":
            apply_to_all_products_boolean = True
        else:
            apply_to_all_products_boolean = False

        coupon_amount = request.POST.get("coupon-amount")

        allow_free_shipping_boolean = False
        allow_free_shipping = request.POST.get("allow-free-shipping")
        if allow_free_shipping == "on":
            allow_free_shipping_boolean = True
        else:
            allow_free_shipping_boolean = False

        coupon_expiry_date = request.POST.get("coupon-expiry-date")

        minimum_spend = request.POST.get("minimum-spend")

        maximum_spend = request.POST.get("maximum-spend")

        individual_use_only_formatted = False
        individual_use_only = request.POST.get("individual-use-only")
        if individual_use_only == "on":
            individual_use_only_formatted = True

        exclude_sale_items_formatted = False
        exclude_sale_items = request.POST.get("exclude-sale-items")
        if exclude_sale_items == "on":
            exclude_sale_items_formatted = True

        try:
            day = int(coupon_expiry_date[0:2])
            month = int(coupon_expiry_date[3:5])
            year = int(coupon_expiry_date[6:])
            coupon_expiry_date_formatted = date(year, month, day)
        except:
            coupon_expiry_date_formatted = date.today()

        email_restrictions = request.POST.get("email-restrictions")

        usage_limit_per_coupon = request.POST.get("usage-limit-per-coupon")
        if usage_limit_per_coupon == "":
            usage_limit_per_coupon_formatted = 1
        else:
            usage_limit_per_coupon_formatted = int(usage_limit_per_coupon)

        usage_limit_per_item = request.POST.get("usage-limit-per-item")
        if usage_limit_per_item == "":
            usage_limit_per_item_formatted = 1
        else:
            usage_limit_per_item_formatted = int(usage_limit_per_item)

        usage_limit_per_user = request.POST.get("usage-limit-per-user")
        if usage_limit_per_user == "":
            usage_limit_per_user_formatted = 1
        else:
            usage_limit_per_user_formatted = int(usage_limit_per_user)

        username = request.session["username"]
        user = UserDatabase.objects.get(username=username)
        seller_id = user.id

        try:
            prevCoupon = Coupon.objects.get(seller_id=seller_id)
        except:
            prevCoupon = None

        if prevCoupon is None:
            coupon = Coupon(
                seller_id=seller_id,
                code=coupon_code,
                description=coupon_description,
                discount_type=discount_type,
                apply_to_all_products=apply_to_all_products_boolean,
                coupon_amount=coupon_amount,
                allow_free_shipping=allow_free_shipping_boolean,
                coupon_expiry=coupon_expiry_date_formatted,
                minimum_spend=minimum_spend,
                maximum_spend=maximum_spend,
                individual_use_only=individual_use_only_formatted,
                exclude_sale_item=exclude_sale_items_formatted,
                restricted_emails=email_restrictions,
                usage_limit_per_coupon=usage_limit_per_coupon_formatted,
                usage_limit_item=usage_limit_per_item_formatted,
                usage_limit_per_user=usage_limit_per_user_formatted
            )
            coupon.save()
        else:
            if coupon_code != "":
                prevCoupon.code = coupon_code

            if coupon_description != "":
                prevCoupon.description = coupon_description

            if discount_type != "":
                prevCoupon.discount_type = discount_type

            prevCoupon.apply_to_all_products = apply_to_all_products_boolean

            if coupon_amount != "":
                prevCoupon.coupon_amount = coupon_amount

            prevCoupon.allow_free_shipping = allow_free_shipping_boolean

            prevCoupon.coupon_expiry= coupon_expiry_date_formatted

            prevCoupon.minimum_spend = minimum_spend

            prevCoupon.maximum_spend = maximum_spend

            prevCoupon.individual_use_only = individual_use_only_formatted

            prevCoupon.exclude_sale_item = exclude_sale_items_formatted

            prevCoupon.restricted_emails = email_restrictions

            prevCoupon.usage_limit_per_coupon = usage_limit_per_coupon_formatted

            prevCoupon.usage_limit_item = usage_limit_per_item_formatted

            prevCoupon.usage_limit_per_user = usage_limit_per_user_formatted

            prevCoupon.save()

        coupon_added = True
    try:
        coupon_id = request.GET.get("coupon_id")
        coupon = Coupon.objects.get(id=coupon_id)
        serialized_coupon = CouponSerializer(coupon)
    except:
        coupon = None
        serialized_coupon = None

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
                "coupon_added": coupon_added,
                "coupon": serialized_coupon,
                "category": serialized_categories,
                "cart_total": cart_total
            }

    return Response(params)

def proStore(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    seller = UserDatabase.objects.get(username=username)
    seller_id = seller.id

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1


    try:
        allProducts = Product.objects.filter(seller_id=seller_id)
    except:
        allProducts = None

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    try:
        store = Store.objects.get(seller_id=seller_id)
    except:
        store = None


    categories = Category.objects.all()
    params = {
        "categories": categories,
        "products": products,
        "store": store,
        "next_page": next_page,
        "prev_page": prev_page,
        "cart_total": cart_total
    }
    return render(request, 'proStore.html', params)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def proStoreApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    seller = UserDatabase.objects.get(username=username)
    seller_id = seller.id

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    try:
        allProducts = Product.objects.filter(seller_id=seller_id)
    except:
        allProducts = None

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    try:
        store = Store.objects.get(seller_id=seller_id)
        serialized_store = StoreSerializer(store)
    except:
        store = None
        serialized_store = None

    serialized_products = ProductSerializer(products, many=True)
    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "categories": serialized_categories,
        "products": serialized_products,
        "store": serialized_store,
        "next_page": next_page,
        "prev_page": prev_page,
        "cart_total": cart_total
    }
    return Response(params)

def categoryPage(request):

    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    category = request.GET.get('category')
    categoryDB = Category.objects.get(name=category)
    categoryID = categoryDB.id

    subCategories = SubCategory.objects.filter(category_id=categoryID)

    categories = Category.objects.all()
    params = {
        'sub_categories': subCategories,
        'category': category,
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'categoryPage.html', params)

@api_view(["GET"])
def categoryPageApi(request):
    try:
        user = request.user
        username = user.name
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    category = request.GET.get('category')
    serialized_category = CategorySerializer(category)
    categoryDB = Category.objects.get(name=category)
    categoryID = categoryDB.id

    subCategories = SubCategory.objects.filter(category_id=categoryID)
    serialized_sub_categories = SubCategorySerializer(subCategories, many=True)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        'sub_categories': serialized_sub_categories,
        'category': serialized_category,
        "categories": serialized_categories,
        "cart_total": cart_total
    }
    return Response(params)

def shopPage(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    allProducts = Product.objects.all()

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    categories = Category.objects.all()
    params = {
        "products": products,
        "next_page": next_page,
        "prev_page": prev_page,
        "categories":categories,
        "cart_total": cart_total
    }

    return render(request, 'shop.html', params)

@api_view(["GET"])
def shopPageApi(request):
    try:
        user = request.user
        username = user.name
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    allProducts = Product.objects.all()

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    serialized_products = ProductSerializer(products, many=True)

    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "products": serialized_products,
        "next_page": next_page,
        "prev_page": prev_page,
        "categories": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def productPage(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    review_updated = False
    if request.method != "POST":
        product_id = request.GET.get('product_id')
    else:

        try:
            username = request.session["username"]
        except:
            return redirect("loginPage")

        product_id = request.POST.get("product_id")

        comment = request.POST.get("comment")
        rating_value = request.POST.get("rating")

        if comment != "":
            userComment = UserComment(
                username=username,
                product_id=product_id,
                comment=comment
            )
            userComment.save()

        userReview = UserReview(
            product_id=product_id,
            rating=rating_value
        )
        userReview.save()

        review_updated = True

    product = Product.objects.get(id=product_id)
    seller_id = product.seller_id

    seller = UserDatabase.objects.get(id=seller_id)

    store = Store.objects.get(seller_id=seller_id)

    category = product.category_id
    related_products = Product.objects.filter(category_id=category)

    ratings = UserReview.objects.filter(product_id=product_id)

    total_rating = 0.0
    count = 0
    for rating in ratings:
        total_rating += float(rating.rating)
        count += 1
    if count != 0:
        total_rating /= float(count)

    shipping = Shipping.objects.filter(seller_id=seller_id)

    print(store.store_banner)

    comments = UserComment.objects.filter(product_id=product_id)

    categories = Category.objects.all()
    params = {
        "product": product,
        "seller": seller,
        "store": store,
        "related_products": related_products,
        "total_rating": total_rating,
        "rating_count": count,
        "comments": comments,
        "shipping": shipping,
        "review_updated": review_updated,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request, "product.html", params)

@api_view(["GET"])
def productPageApi(request):
    try:
        user = request.user
        username = user.name
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    review_updated = False
    if request.method != "POST":
        product_id = request.GET.get('product_id')
    else:

        try:
            username = request.session["username"]
        except:
            return redirect("loginPage")

        product_id = request.POST.get("product_id")

        comment = request.POST.get("comment")
        rating_value = request.POST.get("rating")

        if comment != "":
            userComment = UserComment(
                username=username,
                product_id=product_id,
                comment=comment
            )
            userComment.save()

        userReview = UserReview(
            product_id=product_id,
            rating=rating_value
        )
        userReview.save()

        review_updated = True

    product = Product.objects.get(id=product_id)
    seller_id = product.seller_id

    seller = UserDatabase.objects.get(id=seller_id)

    store = Store.objects.get(seller_id=seller_id)

    category = product.category_id
    related_products = Product.objects.filter(category_id=category)

    ratings = UserReview.objects.filter(product_id=product_id)

    total_rating = 0.0
    count = 0
    for rating in ratings:
        total_rating += float(rating.rating)
        count += 1
    if count != 0:
        total_rating /= float(count)

    shipping = Shipping.objects.filter(seller_id=seller_id)

    print(store.store_banner)

    comments = UserComment.objects.filter(product_id=product_id)

    categories = Category.objects.all()

    serialized_product = ProductSerializer(product)
    serialized_seller = UserDatabaseSerializer(seller)
    serialized_store = StoreSerializer(store)
    serialized_related_products = ProductSerializer(related_products, many=True)
    serialized_comments = UserCommentSerializer(comments, many=True)
    serialized_shipping = ShippingSerializer(shipping, many=True)
    params = {
        "product": serialized_product,
        "seller": serialized_seller,
        "store": serialized_store,
        "related_products": serialized_related_products,
        "total_rating": total_rating,
        "rating_count": count,
        "comments": serialized_comments,
        "shipping": serialized_shipping,
        "review_updated": review_updated,
        "categories": categories,
        "cart_total": cart_total
    }

    return Response(params)

def addToCart(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if request.method == "POST":
        quantity = request.POST.get("quantity")
        if quantity == "":
            quantity = 1
        product_id = request.POST.get("product_id")

        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id

        try:
            presentCart = Cart.objects.get(buyer_id=buyer_id, product_id=product_id)
        except:
            presentCart = None

        if presentCart is None:
            cart = Cart(
                buyer_id=buyer_id,
                product_id=product_id,
                product_quantity=quantity
            )
            cart.save()
        else:
            qty = presentCart.product_quantity
            qty += quantity
            presentCart.product_quantity = qty
            presentCart.save()

    return redirect("cartPage")

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def addToCartApi(request):
    user = request.user
    username = user.name

    if request.method == "POST":
        quantity = request.POST.get("quantity")
        if quantity == "":
            quantity = 1
        product_id = request.POST.get("product_id")

        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id

        try:
            presentCart = Cart.objects.get(buyer_id=buyer_id, product_id=product_id)
        except:
            presentCart = None

        if presentCart is None:
            cart = Cart(
                buyer_id=buyer_id,
                product_id=product_id,
                product_quantity=quantity
            )
            cart.save()
        else:
            qty = presentCart.product_quantity
            qty += quantity
            presentCart.product_quantity = qty
            presentCart.save()

    return Response({
        "status_code": 200,
        "message": "You have successfully added the new product"
    })

def addToGuestCart(request):
    try:
        session_id = request.session["session_id"]
    except:
        session_id = None
    
    if session_id is None:
        session_id = random()
        request.session["session_id"] = session_id
        
    
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")
        if quantity == "":
            quantity = 1

        try:
            presentGuestCart = GuestCart.objects.get(product_id=product_id, session_id=session_id)
        except:
            presentGuestCart = None

        if presentGuestCart is None:
            guest_cart = GuestCart(
                product_id = product_id,
                product_quantity = quantity,
                session_id = session_id
            )
            guest_cart.save()
        else:
            present_quantity = presentGuestCart.product_quantity
            present_quantity += quantity
            presentGuestCart.product_quantity = present_quantity
            presentGuestCart.save()
    
    return redirect('GuestCartPage')

@api_view(["POST"])
def addToGuestCartApi(request):
    try:
        session_id = request.session["session_id"]
    except:
        session_id = None
    
    if session_id is None:
        session_id = random()
        request.session["session_id"] = session_id
        
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")
        if quantity == "":
            quantity = 1

        try:
            presentGuestCart = GuestCart.objects.get(product_id=product_id, session_id=session_id)
        except:
            presentGuestCart = None

        if presentGuestCart is None:
            guest_cart = GuestCart(
                product_id = product_id,
                product_quantity = quantity,
                session_id = session_id
            )
            guest_cart.save()
        else:
            present_quantity = presentGuestCart.product_quantity
            present_quantity += quantity
            presentGuestCart.product_quantity = present_quantity
            presentGuestCart.save()
    
    return Response({
        "status_code": 200,
        "message": "You have successfully added teh product to guest cart"
    })

def cartPage(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id

    item_deleted = False
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        delete_cart_item = Cart.objects.get(buyer_id=buyer_id, product_id=product_id)
        delete_cart_item.delete()
        item_deleted = True

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    allProducts = []
    cart_total = 0.0
    for cart_item in cart_items:
        product_id = cart_item.product_id
        product = Product.objects.get(id=product_id)
        productData = {
            "product": product,
            "quantity": cart_item.product_quantity
        }
        allProducts.append(productData)
        cart_total += float(product.sale_price)

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    categories = Category.objects.all()
    params = {
        "cart_items": products,
        "next_page": next_page,
        "prev_page": prev_page,
        "item_deleted": item_deleted,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request, 'cartPage.html', params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def cartPageApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id

    item_deleted = False
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        delete_cart_item = Cart.objects.get(buyer_id=buyer_id, product_id=product_id)
        delete_cart_item.delete()
        item_deleted = True

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    allProducts = []
    cart_total = 0.0
    for cart_item in cart_items:
        product_id = cart_item.product_id
        product = Product.objects.get(id=product_id)
        productData = {
            "product": product,
            "quantity": cart_item.product_quantity
        }
        allProducts.append(productData)
        cart_total += float(product.sale_price)

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    serialized_products = ProductSerializer(products, many=True)
    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "cart_items": serialized_products,
        "next_page": next_page,
        "prev_page": prev_page,
        "item_deleted": item_deleted,
        "categories": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def GuestCartPage(request):
    try:
        session_id = request.session["session_id"]
    except:
        return redirect("shopPage")

    cart_total = 0.00

    item_deleted = False
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        delete_cart_item = GuestCart.objects.get(session_id=session_id, product_id=product_id)
        delete_cart_item.delete()
        item_deleted = True

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    cart_items = GuestCart.objects.filter(session_id=session_id)

    allProducts = []
    cart_total = 0.0
    for cart_item in cart_items:
        product_id = cart_item.product_id
        product = Product.objects.get(id=product_id)
        productData = {
            "product": product,
            "quantity": cart_item.product_quantity
        }
        allProducts.append(productData)
        cart_total += float(product.sale_price)

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    categories = Category.objects.all()
    params = {
        "cart_items": products,
        "next_page": next_page,
        "prev_page": prev_page,
        "item_deleted": item_deleted,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request, 'cartPage.html', params)

@api_view(["POST"])
def GuestCartPageApi(request):
    try:
        session_id = request.session["session_id"]
    except:
        return redirect("shopPage")

    cart_total = 0.00

    item_deleted = False
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        delete_cart_item = GuestCart.objects.get(session_id=session_id, product_id=product_id)
        delete_cart_item.delete()
        item_deleted = True

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    cart_items = GuestCart.objects.filter(session_id=session_id)

    allProducts = []
    cart_total = 0.0
    for cart_item in cart_items:
        product_id = cart_item.product_id
        product = Product.objects.get(id=product_id)
        productData = {
            "product": product,
            "quantity": cart_item.product_quantity
        }
        allProducts.append(productData)
        cart_total += float(product.sale_price)

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    categories = Category.objects.all()
    serialized_products = ProductSerializer(categories, many=True)
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "cart_items": serialized_products,
        "next_page": next_page,
        "prev_page": prev_page,
        "item_deleted": item_deleted,
        "categories": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def wishlist(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    item_deleted = False

    if request.method == "POST":
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        product_id = request.POST.get("product_id")

        wishlistItem = Wishlist.objects.get(buyer_id=buyer_id, product_id=product_id)
        wishlistItem.delete()

        item_deleted = True

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    wishlist_items = Wishlist.objects.filter(buyer_id=buyer_id)

    allProducts = []

    for wishlist_item in wishlist_items:
        product_id = wishlist_item.product_id
        product = Product.objects.get(id=product_id)
        productData = {
            "product": product
        }
        allProducts.append(productData)

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    categories = Category.objects.all()
    params = {
        "wishlist_items": products,
        "next_page": next_page,
        "prev_page": prev_page,
        "item_deleted": item_deleted,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request, 'wishlistPage.html', params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def wishlistApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    item_deleted = False

    if request.method == "POST":
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        product_id = request.POST.get("product_id")

        wishlistItem = Wishlist.objects.get(buyer_id=buyer_id, product_id=product_id)
        wishlistItem.delete()

        item_deleted = True

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id

    page = request.GET.get('page-number')
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    wishlist_items = Wishlist.objects.filter(buyer_id=buyer_id)

    allProducts = []

    for wishlist_item in wishlist_items:
        product_id = wishlist_item.product_id
        product = Product.objects.get(id=product_id)
        productData = {
            "product": product
        }
        allProducts.append(productData)

    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    categories = Category.objects.all()
    serialized_products = ProductSerializer(products, many=True)
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "wishlist_items": serialized_products,
        "next_page": next_page,
        "prev_page": prev_page,
        "item_deleted": item_deleted,
        "categories": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def addToWishlist(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    if request.method == "POST":
        product_id = request.POST.get("product_id")

        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id

        try:
            presentCart = Wishlist.objects.get(buyer_id=buyer_id, product_id=product_id)
        except:
            presentCart = None

        if presentCart is None:
            wishlist = Wishlist(
                buyer_id=buyer_id,
                product_id=product_id
            )
            wishlist.save()

    return redirect("wishlist")

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def addToWishlistApi(request):
    user = request.user
    username = user.name

    if request.method == "POST":
        product_id = request.POST.get("product_id")

        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id

        try:
            presentCart = Wishlist.objects.get(buyer_id=buyer_id, product_id=product_id)
        except:
            presentCart = None

        if presentCart is None:
            wishlist = Wishlist(
                buyer_id=buyer_id,
                product_id=product_id
            )
            wishlist.save()

    return Response({
        "status_code": 200,
        "message": "Product successfully added to wishlist"
    })

def buyerBillingAddress(request):

    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id

    address_updated = False

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company = request.POST.get("company_name")
        country = request.POST.get("country")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postcode = request.POST.get("postcode")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        try:
            buyerBillingAddress = BuyerBillingAddress.objects.get(user_id=user_id)
        except:
            buyerBillingAddress = None

        if buyerBillingAddress is None:
            billingAddress = BuyerBillingAddress(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                company_name=company,
                country=country,
                address=address,
                city=city,
                state=state,
                postcode=postcode,
                phone=phone,
                email=email
            )
            billingAddress.save()
        else:
            buyerBillingAddress.first_name = first_name
            buyerBillingAddress.last_name = last_name
            buyerBillingAddress.company_name = company
            buyerBillingAddress.country = country
            buyerBillingAddress.address = address
            buyerBillingAddress.city = city
            buyerBillingAddress.state = state
            buyerBillingAddress.postcode = postcode
            buyerBillingAddress.phone = phone
            buyerBillingAddress.email = email

            buyerBillingAddress.save()

        address_updated = True
        print("ADDRES UPDATED")
        print(address_updated)

    states = StoreState.objects.all()

    categories = Category.objects.all()
    params = {
        "states": states,
        "address_updated": address_updated,
        "category": categories,
        "cart_total": cart_total
    }

    return render(request, "buyerBillingAddress.html", params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def buyerBillingAddressApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id

    address_updated = False

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company = request.POST.get("company_name")
        country = request.POST.get("country")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postcode = request.POST.get("postcode")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        try:
            buyerBillingAddress = BuyerBillingAddress.objects.get(user_id=user_id)
        except:
            buyerBillingAddress = None

        if buyerBillingAddress is None:
            billingAddress = BuyerBillingAddress(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                company_name=company,
                country=country,
                address=address,
                city=city,
                state=state,
                postcode=postcode,
                phone=phone,
                email=email
            )
            billingAddress.save()
        else:
            buyerBillingAddress.first_name = first_name
            buyerBillingAddress.last_name = last_name
            buyerBillingAddress.company_name = company
            buyerBillingAddress.country = country
            buyerBillingAddress.address = address
            buyerBillingAddress.city = city
            buyerBillingAddress.state = state
            buyerBillingAddress.postcode = postcode
            buyerBillingAddress.phone = phone
            buyerBillingAddress.email = email

            buyerBillingAddress.save()

        address_updated = True
        print("ADDRES UPDATED")
        print(address_updated)

    states = StoreState.objects.all()
    serialized_states = StoreStateSerializer(states, many=True)
    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "states": serialized_states,
        "address_updated": address_updated,
        "category": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def buyerShippingAddress(request):

    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id

    address_updated = False

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company = request.POST.get("company_name")
        country = request.POST.get("country")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postcode = request.POST.get("postcode")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        try:
            buyerShippingAddress = BuyerAddress.objects.get(user_id=user_id)
        except:
            buyerShippingAddress = None

        if buyerShippingAddress is None:
            shippingAddress = BuyerAddress(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                company_name=company,
                country=country,
                address=address,
                city=city,
                state=state,
                postcode=postcode,
                phone=phone,
                email=email
            )

            shippingAddress.save()
        else:
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.last_name = last_name
            buyerShippingAddress.company_name = company
            buyerShippingAddress.country = country
            buyerShippingAddress.address = address
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name

            buyerShippingAddress.save()

        address_updated = True
        print("IS ADDRESS UPDATED")
        print(address_updated)
    states = StoreState.objects.all()

    categories = Category.objects.all()
    params = {
        "states": states,
        "address_updated": address_updated,
        "category": categories,
        "cart_total": cart_total
    }

    return render(request, "buyerShippingAddress.html", params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def buyerShippingAddressApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    user = UserDatabase.objects.get(username=username)
    user_id = user.id

    address_updated = False

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company = request.POST.get("company_name")
        country = request.POST.get("country")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postcode = request.POST.get("postcode")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        try:
            buyerShippingAddress = BuyerAddress.objects.get(user_id=user_id)
        except:
            buyerShippingAddress = None

        if buyerShippingAddress is None:
            shippingAddress = BuyerAddress(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                company_name=company,
                country=country,
                address=address,
                city=city,
                state=state,
                postcode=postcode,
                phone=phone,
                email=email
            )

            shippingAddress.save()
        else:
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.last_name = last_name
            buyerShippingAddress.company_name = company
            buyerShippingAddress.country = country
            buyerShippingAddress.address = address
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name
            buyerShippingAddress.first_name = first_name

            buyerShippingAddress.save()

        address_updated = True
        print("IS ADDRESS UPDATED")
        print(address_updated)
    states = StoreState.objects.all()
    serialized_states = StoreStateSerializer(states, many=True)
    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    params = {
        "states": serialized_states,
        "address_updated": address_updated,
        "category": serialized_categories,
        "cart_total": cart_total
    }

    return Response(params)

def searchProductPage(request):
    try:
        username = request.session["username"]
    except:
        username = None

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    page = request.GET.get('page-number')
    searchTerm = request.GET.get("search-term")
    category_name = request.GET.get('category')
    print(searchTerm)
    print(category_name)
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    productDatabase = Product.objects.all()

    allProducts = []

    for product in productDatabase:
        category_id = product.category_id
        category = Category.objects.get(id=category_id)
        category_name2 = category.name
        if searchTerm != "":
            if product.name.find(searchTerm):
                if category_name == category_name2:
                    allProducts.append(product)
                    continue
            if product.description.find(searchTerm):
                if category_name == category_name2:
                    allProducts.append(product)
                    continue
            if product.short_description.find(searchTerm):
                if category_name == category_name2:
                    allProducts.append(product)
                    continue
            if product.type.find(searchTerm):
                if category_name == category_name2:
                    allProducts.append(product)
                    continue
        else:
            if category_name == category_name2:
                allProducts.append(product)



    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    categories = Category.objects.all()
    params = {
        "products": products,
        "next_page": next_page,
        "prev_page": prev_page,
        "categories": categories,
        "allProducts": allProducts,
        "searchTerm": searchTerm,
        "cart_total": cart_total
    }

    return render(request, 'shop2.html', params)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def searchProductPageApi(request):
    user = request.user
    username = user.name

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    page = request.GET.get('page-number')
    searchTerm = request.GET.get("search-term")
    category_name = request.GET.get('category')
    print(searchTerm)
    print(category_name)
    page_number = 0
    if page == None:
        page_number = 1
    else:
        page_number = int(page)

    prev_page = 0
    next_page = 0

    if page_number != 1:
        prev_page = page_number - 1

    productDatabase = Product.objects.all()

    allProducts = []

    for product in productDatabase:
        category_id = product.category_id
        category = Category.objects.get(id=category_id)
        category_name2 = category.name
        if searchTerm != "":
            if product.name.find(searchTerm):
                if category_name == category_name2:
                    allProducts.append(product)
                    continue
            if product.description.find(searchTerm):
                if category_name == category_name2:
                    allProducts.append(product)
                    continue
            if product.short_description.find(searchTerm):
                if category_name == category_name2:
                    allProducts.append(product)
                    continue
            if product.type.find(searchTerm):
                if category_name == category_name2:
                    allProducts.append(product)
                    continue
        else:
            if category_name == category_name2:
                allProducts.append(product)



    start_index = (page_number - 1) * 2
    end_index = start_index + 2

    products = []
    if end_index >= len(allProducts):
        products = allProducts[start_index:]
    else:
        products = allProducts[start_index:end_index]
        next_page = page_number + 1

    categories = Category.objects.all()
    serialized_products = ProductSerializer(products, many=True)
    serialized_categories = CategorySerializer(categories, many=True)
    serialized_all_products = ProductSerializer(allProducts, many=True)
    params = {
        "products": serialized_products,
        "next_page": next_page,
        "prev_page": prev_page,
        "categories": serialized_categories,
        "allProducts": serialized_all_products,
        "searchTerm": searchTerm,
        "cart_total": cart_total
    }

    return Response(params)

def checkoutSummary(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    product_id = request.GET.get("product_id")
    product = Product.objects.get(id=product_id)
    quantity = request.GET.get("quantity")
    buyer_states = BuyerState.objects.all()

    amount = float(product.sale_price) * float(quantity)
    tax_percentage = 0.00
    if product.tax_status == "Taxable":
        try:
            tax = AdminTaxRules.objects.get()
        except:
            tax = None
        if tax is not None:
            if product.tax_class == "Standard":
                amount += float(tax.standard_class_tax_percentage) * amount
                tax_percentage = float(tax.standard_class_tax_percentage)
            elif product.tax_class == "Reduced Rate":
                amount += float(tax.reduced_rate_class_tax_percentage) * amount
                tax_percentage = float(tax.reduced_rate_class_tax_percentage)


    params = {
        "product": product,
        "quantity": quantity,
        "states": buyer_states,
        "amount": amount,
        "tax": tax_percentage
    }

    return render(request, "checkoutSummary.html", params)

def checkout(request):
    print("PRODUCT CHECKOUT")
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    first_name = request.POST.get("first-name")
    last_name = request.POST.get("last-name")
    company_name = request.POST.get("company-name")
    country = request.POST.get("country")
    address = request.POST.get("address")
    city = request.POST.get("city")
    state = request.POST.get("state")
    postCode = request.POST.get("postcode")
    phone = request.POST.get("phone")
    email = request.POST.get("email")
    product_id = request.POST.get("product_id")
    quantity = request.POST.get("quantity")
    amount = float(request.POST.get("amount"))
    tax = float(request.POST.get("tax"))
    coupon_code = request.POST.get("coupon-code")

    shipping = "NATIONAL"

    disabled = False
    if country != "United States (US)":
        shipping = "INTERNATIONAL"

    product = Product.objects.get(id=product_id)
    seller_id = product.seller_id
    try:
        seller = Shipping.objects.get(seller_id=seller_id)

        if shipping == "NATIONAL":
            if seller.disable_national_shipping == "on":
                disabled = True
                params = {
                    "disabled": disabled,
                }
                return render(request, "checkoutSummary.html", params)
            else:
                if seller.national_free_shipping_enabled != "on":
                    amount += float(seller.national_shipping_fee)
        else:
            if seller.disable_international_shipping == "on":
                disabled = True
                params = {
                    "disabled": disabled,
                }
                return render(request, "checkoutSummary.html", params)
            else:
                if seller.international_free_shipping_enabled != "on":
                    amount += float(seller.international_shipping_fee)
    except:
        print()


    adminPaymentDetails = AdminPaymentDetail.objects.get()

    stripe.api_key = adminPaymentDetails.stripe_private_key

    key = adminPaymentDetails.stripe_public_key

    try:
        coupon = Coupon.objects.get(code=coupon_code)
        coupon_amount = float(coupon.coupon_amount)
        amount -= coupon_amount
    except:
        print()

    total_tax = tax * amount
    amount_int = int(amount * 100)

    params = {
        "amount_int": amount_int,
        "amount": amount,
        "key": key,
        "product": product,
        "quantity": quantity,
        "cart_total": cart_total,
        "first_name": first_name,
        "last_name": last_name,
        "country": country,
        "address": address,
        "city": city,
        "state": state,
        "postcode": postCode,
        "phone": phone,
        "email": email,
        "total_tax": total_tax
    }

    return render(request, "checkout.html", params)

def charge(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        amount_int = int(amount * 100)
        charge = stripe.Charge.create(
            amount=amount_int,
            currency="inr",
            description="Payment Gateway",
            source=request.POST["stripeToken"]
        )

        total_cost = float(amount_int) / 100

        product_id = request.POST.get("product_id")
        product = Product.objects.get(id=product_id)
        category_id = product.category_id
        category = Category.objects.get(id=category_id)
        category_name = category.name
        seller_id = product.seller_id
        seller = UserDatabase.objects.get(id=seller_id)
        seller_name = seller.username
        buyer = UserDatabase.objects.get(username=username)
        buyer_id = buyer.id
        buyer_name=buyer.username

        payment = SellerPaymentDetail.objects.get(seller_id=seller_id)
        quantity=request.POST.get('quantity')

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        country = request.POST.get("country")
        address = request.POST.get("address")
        state = request.POST.get("state")
        city = request.POST.get("city")
        postcode = request.POST.get("postcode")
        phone=request.POST.get("phone")
        email = request.POST.get("email")
        total_tax = request.POST.get("total_tax")

        order = Order(
            seller_id=seller_id,
            seller_name=seller_name,
            seller_paypal=payment.paypal_address,
            buyer_id=buyer_id,
            buyer_name=buyer_name,
            product_id = product.id,
            product_name=product.name,
            product_description=product.description,
            product_short_description=product.short_description,
            product_category_name=category_name,
            product_image1=product.image1,
            product_image2=product.image2,
            product_image3=product.image3,
            product_price=product.price,
            product_sale_price=product.sale_price,
            product_tax_status=product.tax_status,
            product_tax_class=product.tax_class,
            currency="$",
            quantity=quantity,
            first_name=first_name,
            last_name=last_name,
            country=country,
            address=address,
            state=state,
            city=city,
            postcode=postcode,
            phone=phone,
            email=email,
            total_cost=total_cost,
            total_tax=total_tax
        )
        order.save()

        cart_item = Cart.objects.get(product_id=product.id, buyer_id=buyer_id)
        cart_item.delete()

        admin = UserDatabase.objects.get(user_type="ADMIN")
        admin_email = admin.email
        seller = UserDatabase.objects.get(id=seller_id)
        seller_email = seller.email
        send_mail(
            'New Orders on ehomespun.com',
            'You have new multiple orders on ehomespun.com. Please login to check.',
            admin_email,
            [seller_email],
            fail_silently=False,
        )

    return redirect("ordersPage")

def checkoutAllSummary(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    total_amount = 0.00
    products = []
    total_tax = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        product = Product.objects.get(id=product_id)
        quantity = cart_item.product_quantity
        buyer_states = BuyerState.objects.all()

        amount = float(product.sale_price) * float(quantity)
        tax_percentage = 0.00
        if product.tax_status == "Taxable":
            try:
                tax = AdminTaxRules.objects.get()
            except:
                tax = None
            if tax is not None:
                if product.tax_class == "Standard":
                    amount += float(tax.standard_class_tax_percentage) * amount
                    total_tax += float(tax.standard_class_tax_percentage) * amount
                    tax_percentage = tax.standard_class_tax_percentage
                elif product.tax_class == "Reduced Rate":
                    amount += float(tax.reduced_rate_class_tax_percentage) * amount
                    total_tax += float(tax.standard_class_tax_percentage) * amount
                    tax_percentage = tax.reduced_rate_class_tax_percentage

        total_amount += amount
        product_data = {
            "product": product,
            "quantity": quantity,
            "tax": tax_percentage,
            "amount": amount
        }
        products.append(product_data)


    params = {
        "products_data": products,
        "states": buyer_states,
        "total_amount": total_amount,
        "total_tax": total_tax
    }

    return render(request, "checkoutSummaryAll.html", params)

def checkoutAll(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    frontend_products = []
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)
        product = Product.objects.get(id=product_id)
        frontend_data = {
            "product": product,
            "quantity": cart_item.product_quantity,
        }
        frontend_products.append(frontend_data)

    first_name = request.POST.get("first-name")
    last_name = request.POST.get("last-name")
    company_name = request.POST.get("company-name")
    country = request.POST.get("country")
    address = request.POST.get("address")
    city = request.POST.get("city")
    state = request.POST.get("state")
    postCode = request.POST.get("postcode")
    phone = request.POST.get("phone")
    email = request.POST.get("email")
    total_amount = float(request.POST.get("total_amount"))
    coupon_code = request.POST.get("coupon-code")

    for cart_item in cart_items:
        shipping = "NATIONAL"

        disabled = False
        if country != "United States (US)":
            shipping = "INTERNATIONAL"

        product_id = cart_item.product_id
        product = Product.objects.get(id=product_id)
        seller_id = product.seller_id
        amount = float(product.sale_price) * float(cart_item.product_quantity)
        try:
            seller = Shipping.objects.get(seller_id=seller_id)

            if shipping == "NATIONAL":
                if seller.disable_national_shipping == "on":
                    disabled = True
                    params = {
                        "disabled": disabled,
                        "product": product
                    }
                    return render(request, "checkoutSummaryAll.html", params)
                else:
                    if seller.national_free_shipping_enabled != "on":
                        total_amount += float(seller.national_shipping_fee)
            else:
                if seller.disable_international_shipping == "on":
                    disabled = True
                    params = {
                        "disabled": disabled,
                        "product": product
                    }
                    return render(request, "checkoutSummary.html", params)
                else:
                    if seller.international_free_shipping_enabled != "on":
                        total_amount += float(seller.international_shipping_fee)
        except:
            print()




    adminPaymentDetails = AdminPaymentDetail.objects.get()

    stripe.api_key = adminPaymentDetails.stripe_private_key

    key = adminPaymentDetails.stripe_public_key

    try:
        coupon = Coupon.objects.get(code=coupon_code)
        coupon_amount = float(coupon.coupon_amount)
        amount -= coupon_amount
    except:
        print()

    amount_int = int(total_amount * 100)

    params = {
        "amount_int": amount_int,
        "amount": total_amount,
        "key": key,
        "cart_total": cart_total,
        "first_name": first_name,
        "last_name": last_name,
        "country": country,
        "address": address,
        "city": city,
        "state": state,
        "postcode": postCode,
        "phone": phone,
        "email": email,
        "products": frontend_products
    }

    return render(request, "checkoutAll.html", params)

def chargeAll(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        amount_int = int(amount * 100)
        charge = stripe.Charge.create(
            amount=amount_int,
            currency="inr",
            description="Payment Gateway",
            source=request.POST["stripeToken"]
        )

        for cart_item in cart_items:
            product_id = cart_item.product_id
            product = Product.objects.get(id=product_id)
            category_id = product.category_id
            category = Category.objects.get(id=category_id)
            category_name = category.name
            seller_id = product.seller_id
            seller = UserDatabase.objects.get(id=seller_id)
            seller_name = seller.username
            buyer = UserDatabase.objects.get(username=username)
            buyer_id = buyer.id
            buyer_name=buyer.username

            payment = SellerPaymentDetail.objects.get(seller_id=seller_id)
            quantity=cart_item.product_quantity

            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            country = request.POST.get("country")
            address = request.POST.get("address")
            state = request.POST.get("state")
            city = request.POST.get("city")
            postcode = request.POST.get("postcode")
            phone=request.POST.get("phone")
            email = request.POST.get("email")

            tax_percentage = 0.00
            if product.tax_status == "Taxable":
                try:
                    tax = AdminTaxRules.objects.get()
                except:
                    tax = None
                if tax is not None:
                    if product.tax_class == "Standard":
                        tax_percentage = float(tax.standard_class_tax_percentage)
                    elif product.tax_class == "Reduced Rate":
                        tax_percentage = float(tax.reduced_rate_class_tax_percentage)
            total_tax = tax_percentage * float(product.sale_price)
            total_cost = float(product.sale_price) + total_tax

            order = Order(
                seller_id=seller_id,
                seller_name=seller_name,
                seller_paypal=payment.paypal_address,
                buyer_id=buyer_id,
                buyer_name=buyer_name,
                product_id = product.id,
                product_name=product.name,
                product_description=product.description,
                product_short_description=product.short_description,
                product_category_name=category_name,
                product_image1=product.image1,
                product_image2=product.image2,
                product_image3=product.image3,
                product_price=product.price,
                product_sale_price=product.sale_price,
                product_tax_status=product.tax_status,
                product_tax_class=product.tax_class,
                currency="$",
                quantity=quantity,
                first_name=first_name,
                last_name=last_name,
                country=country,
                address=address,
                state=state,
                city=city,
                postcode=postcode,
                phone=phone,
                email=email,
                total_cost=total_cost,
                total_tax=total_tax
            )
            order.save()


            cart_item = Cart.objects.get(product_id=product.id)
            cart_item.delete()

        admin = UserDatabase.objects.get(user_type="ADMIN")
        admin_email = admin.email
        seller = UserDatabase.objects.get(id=seller_id)
        seller_email = seller.email
        send_mail(
            'New Orders on ehomespun.com',
            'You have new multiple orders on ehomespun.com. Please login to check.',
            admin_email,
            [seller_email],
            fail_silently=False,
        )

    return redirect("ordersPage")

def checkoutMembership(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    frontend_products = []
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)
        product = Product.objects.get(id=product_id)
        frontend_data = {
            "product": product,
            "quantity": cart_item.product_quantity,
        }
        frontend_products.append(frontend_data)

    membership_type = request.POST.get("membership-type")
    membership_price = float(request.POST.get("membership-price"))

    adminPaymentDetails = AdminPaymentDetail.objects.get()

    stripe.api_key = adminPaymentDetails.stripe_private_key

    key = adminPaymentDetails.stripe_public_key

    params = {
        "key": key,
        "cart_total": cart_total,
        "amount": membership_price,
        "membership_type": membership_type
    }

    return render(request, "checkoutMembership.html", params)

def chargeMembership(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    cart_total = 0.00

    if username is not None:
        user = UserDatabase.objects.get(username=username)
        buyer_id = user.id
        cart_items = Cart.objects.filter(buyer_id=buyer_id)

        cart_total = 0.00
        for cart_item in cart_items:
            product_id = cart_item.product_id
            quantity = cart_item.product_quantity
            cart_product = Product.objects.get(id=product_id)
            price = cart_product.sale_price
            cart_total += float(price * quantity)

    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        amount_int = int(amount * 100)
        charge = stripe.Charge.create(
            amount=amount_int,
            currency="inr",
            description="Payment Gateway",
            source=request.POST["stripeToken"]
        )
        membership_type = request.POST.get("membership-type")

        user = UserDatabase.objects.get(username=username)
        user_id = user.id

        try:
            store = Store.objects.get(seller_id=user_id)
        except:
            store = None

        if store is not None:
            store.membership_status = "active"
            store.membership_type = membership_type
            store.membership_start_date = date.today()

            store.save()
        else:
            store = Store(
                membership_status="active",
                membership_type=membership_type,
                membership_start_date=date.today()
            )
            store.save()

    return redirect("proDashboard")

def requestRefund(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    order_id = request.POST.get('product_id')
    order = Order.objects.get(id=order_id)
    order.refund_status = "APPLIED"
    order.save()

    return redirect("userDashboard")

def orderDetailsPage(request):
    try:
        username = request.session["username"]
    except:
        logout(request)
        return redirect("loginPage")

    user = UserDatabase.objects.get(username=username)
    buyer_id = user.id
    cart_items = Cart.objects.filter(buyer_id=buyer_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    order_id = request.GET.get("product_id")

    order = Order.objects.get(id=order_id)

    params = {
        "cart_total": cart_total,
        "order": order
    }

    return render(request, "orderDetails.html", params)

def guestCheckoutSummary(request):
    try:
        session_id = request.session["session_id"]
    except:
        return redirect("shopPage")

    product_id = request.GET.get("product_id")
    product = Product.objects.get(id=product_id)
    quantity = request.GET.get("quantity")
    buyer_states = BuyerState.objects.all()

    amount = float(product.sale_price) * float(quantity)
    tax_percentage = 0.00
    if product.tax_status == "Taxable":
        try:
            tax = AdminTaxRules.objects.get()
        except:
            tax = None
        if tax is not None:
            if product.tax_class == "Standard":
                amount += float(tax.standard_class_tax_percentage) * amount
                tax_percentage = float(tax.standard_class_tax_percentage)
            elif product.tax_class == "Reduced Rate":
                amount += float(tax.reduced_rate_class_tax_percentage) * amount
                tax_percentage = float(tax.reduced_rate_class_tax_percentage)


    params = {
        "product": product,
        "quantity": quantity,
        "states": buyer_states,
        "amount": amount,
        "tax": tax_percentage
    }

    return render(request, "checkoutSummary.html", params)

def guestCheckout(request):
    print("PRODUCT CHECKOUT")
    try:
        session_id = request.session["session_id"]
    except:
        return redirect("shopPage")

    cart_items = GuestCart.objects.filter(session_id=session_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    first_name = request.POST.get("first-name")
    last_name = request.POST.get("last-name")
    company_name = request.POST.get("company-name")
    country = request.POST.get("country")
    address = request.POST.get("address")
    city = request.POST.get("city")
    state = request.POST.get("state")
    postCode = request.POST.get("postcode")
    phone = request.POST.get("phone")
    email = request.POST.get("email")
    product_id = request.POST.get("product_id")
    quantity = request.POST.get("quantity")
    amount = float(request.POST.get("amount"))
    tax = float(request.POST.get("tax"))
    coupon_code = request.POST.get("coupon-code")

    shipping = "NATIONAL"

    disabled = False
    if country != "United States (US)":
        shipping = "INTERNATIONAL"

    product = Product.objects.get(id=product_id)
    seller_id = product.seller_id
    try:
        seller = Shipping.objects.get(seller_id=seller_id)

        if shipping == "NATIONAL":
            if seller.disable_national_shipping == "on":
                disabled = True
                params = {
                    "disabled": disabled,
                }
                return render(request, "checkoutSummary.html", params)
            else:
                if seller.national_free_shipping_enabled != "on":
                    amount += float(seller.national_shipping_fee)
        else:
            if seller.disable_international_shipping == "on":
                disabled = True
                params = {
                    "disabled": disabled,
                }
                return render(request, "checkoutSummary.html", params)
            else:
                if seller.international_free_shipping_enabled != "on":
                    amount += float(seller.international_shipping_fee)
    except:
        print()


    adminPaymentDetails = AdminPaymentDetail.objects.get()

    stripe.api_key = adminPaymentDetails.stripe_private_key

    key = adminPaymentDetails.stripe_public_key

    try:
        coupon = Coupon.objects.get(code=coupon_code)
        coupon_amount = float(coupon.coupon_amount)
        amount -= coupon_amount
    except:
        print()

    total_tax = tax * amount
    amount_int = int(amount * 100)

    params = {
        "amount_int": amount_int,
        "amount": amount,
        "key": key,
        "product": product,
        "quantity": quantity,
        "cart_total": cart_total,
        "first_name": first_name,
        "last_name": last_name,
        "country": country,
        "address": address,
        "city": city,
        "state": state,
        "postcode": postCode,
        "phone": phone,
        "email": email,
        "total_tax": total_tax
    }

    return render(request, "checkout.html", params)

def charge(request):
    try:
        session_id = request.session["session_id"]
    except:
        return redirect("shopPage")

    cart_items = GuestCart.objects.filter(session_id=session_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        amount_int = int(amount * 100)
        charge = stripe.Charge.create(
            amount=amount_int,
            currency="inr",
            description="Payment Gateway",
            source=request.POST["stripeToken"]
        )

        total_cost = float(amount_int) / 100

        product_id = request.POST.get("product_id")
        product = Product.objects.get(id=product_id)
        category_id = product.category_id
        category = Category.objects.get(id=category_id)
        category_name = category.name
        seller_id = product.seller_id
        seller = UserDatabase.objects.get(id=seller_id)
        seller_name = seller.username

        payment = SellerPaymentDetail.objects.get(seller_id=seller_id)
        quantity=request.POST.get('quantity')

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        country = request.POST.get("country")
        address = request.POST.get("address")
        state = request.POST.get("state")
        city = request.POST.get("city")
        postcode = request.POST.get("postcode")
        phone=request.POST.get("phone")
        email = request.POST.get("email")
        total_tax = request.POST.get("total_tax")

        order = Order(
            seller_id=seller_id,
            seller_name=seller_name,
            seller_paypal=payment.paypal_address,
            product_id = product.id,
            product_name=product.name,
            product_description=product.description,
            product_short_description=product.short_description,
            product_category_name=category_name,
            product_image1=product.image1,
            product_image2=product.image2,
            product_image3=product.image3,
            product_price=product.price,
            product_sale_price=product.sale_price,
            product_tax_status=product.tax_status,
            product_tax_class=product.tax_class,
            currency="$",
            quantity=quantity,
            first_name=first_name,
            last_name=last_name,
            country=country,
            address=address,
            state=state,
            city=city,
            postcode=postcode,
            phone=phone,
            email=email,
            total_cost=total_cost,
            total_tax=total_tax
        )
        order.save()

        cart_item = Cart.objects.get(product_id=product.id, session_id=session_id)
        cart_item.delete()

        admin = UserDatabase.objects.get(user_type="ADMIN")
        admin_email = admin.email
        seller = UserDatabase.objects.get(id=seller_id)
        seller_email = seller.email
        send_mail(
            'New Orders on ehomespun.com',
            'You have new multiple orders on ehomespun.com. Please login to check.',
            admin_email,
            [seller_email],
            fail_silently=False,
        )

    return redirect("shopPage")

def guestCheckoutAllSummary(request):
    try:
        session_id = request.session["session_id"]
    except:
        return redirect("shopPage")

    cart_items = GuestCart.objects.filter(session_id=session_id)

    total_amount = 0.00
    products = []
    total_tax = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        product = Product.objects.get(id=product_id)
        quantity = cart_item.product_quantity
        buyer_states = BuyerState.objects.all()

        amount = float(product.sale_price) * float(quantity)
        tax_percentage = 0.00
        if product.tax_status == "Taxable":
            try:
                tax = AdminTaxRules.objects.get()
            except:
                tax = None
            if tax is not None:
                if product.tax_class == "Standard":
                    amount += float(tax.standard_class_tax_percentage) * amount
                    total_tax += float(tax.standard_class_tax_percentage) * amount
                    tax_percentage = tax.standard_class_tax_percentage
                elif product.tax_class == "Reduced Rate":
                    amount += float(tax.reduced_rate_class_tax_percentage) * amount
                    total_tax += float(tax.standard_class_tax_percentage) * amount
                    tax_percentage = tax.reduced_rate_class_tax_percentage

        total_amount += amount
        product_data = {
            "product": product,
            "quantity": quantity,
            "tax": tax_percentage,
            "amount": amount
        }
        products.append(product_data)


    params = {
        "products_data": products,
        "states": buyer_states,
        "total_amount": total_amount,
        "total_tax": total_tax
    }

    return render(request, "checkoutSummaryAll.html", params)

def guestCheckoutAll(request):
    try:
        session_id = request.session["session_id"]
    except:
        return redirect("shopPage")

    cart_items = GuestCart.objects.filter(session_id=session_id)

    cart_total = 0.00
    frontend_products = []
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)
        product = Product.objects.get(id=product_id)
        frontend_data = {
            "product": product,
            "quantity": cart_item.product_quantity,
        }
        frontend_products.append(frontend_data)

    first_name = request.POST.get("first-name")
    last_name = request.POST.get("last-name")
    company_name = request.POST.get("company-name")
    country = request.POST.get("country")
    address = request.POST.get("address")
    city = request.POST.get("city")
    state = request.POST.get("state")
    postCode = request.POST.get("postcode")
    phone = request.POST.get("phone")
    email = request.POST.get("email")
    total_amount = float(request.POST.get("total_amount"))
    coupon_code = request.POST.get("coupon-code")

    for cart_item in cart_items:
        shipping = "NATIONAL"

        disabled = False
        if country != "United States (US)":
            shipping = "INTERNATIONAL"

        product_id = cart_item.product_id
        product = Product.objects.get(id=product_id)
        seller_id = product.seller_id
        amount = float(product.sale_price) * float(cart_item.product_quantity)
        try:
            seller = Shipping.objects.get(seller_id=seller_id)

            if shipping == "NATIONAL":
                if seller.disable_national_shipping == "on":
                    disabled = True
                    params = {
                        "disabled": disabled,
                        "product": product
                    }
                    return render(request, "checkoutSummaryAll.html", params)
                else:
                    if seller.national_free_shipping_enabled != "on":
                        total_amount += float(seller.national_shipping_fee)
            else:
                if seller.disable_international_shipping == "on":
                    disabled = True
                    params = {
                        "disabled": disabled,
                        "product": product
                    }
                    return render(request, "checkoutSummary.html", params)
                else:
                    if seller.international_free_shipping_enabled != "on":
                        total_amount += float(seller.international_shipping_fee)
        except:
            print()




    adminPaymentDetails = AdminPaymentDetail.objects.get()

    stripe.api_key = adminPaymentDetails.stripe_private_key

    key = adminPaymentDetails.stripe_public_key

    try:
        coupon = Coupon.objects.get(code=coupon_code)
        coupon_amount = float(coupon.coupon_amount)
        amount -= coupon_amount
    except:
        print()

    amount_int = int(total_amount * 100)

    params = {
        "amount_int": amount_int,
        "amount": total_amount,
        "key": key,
        "cart_total": cart_total,
        "first_name": first_name,
        "last_name": last_name,
        "country": country,
        "address": address,
        "city": city,
        "state": state,
        "postcode": postCode,
        "phone": phone,
        "email": email,
        "products": frontend_products
    }

    return render(request, "checkoutAll.html", params)

def guestChargeAll(request):
    try:
        session_id = request.session["session_id"]
    except:
        return redirect("shopPage")

    cart_total = 0.00
    
    cart_items = GuestCart.objects.filter(session_id=session_id)

    cart_total = 0.00
    for cart_item in cart_items:
        product_id = cart_item.product_id
        quantity = cart_item.product_quantity
        cart_product = Product.objects.get(id=product_id)
        price = cart_product.sale_price
        cart_total += float(price * quantity)

    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        amount_int = int(amount * 100)
        charge = stripe.Charge.create(
            amount=amount_int,
            currency="inr",
            description="Payment Gateway",
            source=request.POST["stripeToken"]
        )

        for cart_item in cart_items:
            product_id = cart_item.product_id
            product = Product.objects.get(id=product_id)
            category_id = product.category_id
            category = Category.objects.get(id=category_id)
            category_name = category.name
            seller_id = product.seller_id
            seller = UserDatabase.objects.get(id=seller_id)
            seller_name = seller.username

            payment = SellerPaymentDetail.objects.get(seller_id=seller_id)
            quantity=cart_item.product_quantity

            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            country = request.POST.get("country")
            address = request.POST.get("address")
            state = request.POST.get("state")
            city = request.POST.get("city")
            postcode = request.POST.get("postcode")
            phone=request.POST.get("phone")
            email = request.POST.get("email")

            tax_percentage = 0.00
            if product.tax_status == "Taxable":
                try:
                    tax = AdminTaxRules.objects.get()
                except:
                    tax = None
                if tax is not None:
                    if product.tax_class == "Standard":
                        tax_percentage = float(tax.standard_class_tax_percentage)
                    elif product.tax_class == "Reduced Rate":
                        tax_percentage = float(tax.reduced_rate_class_tax_percentage)
            total_tax = tax_percentage * float(product.sale_price)
            total_cost = float(product.sale_price) + total_tax

            order = Order(
                seller_id=seller_id,
                seller_name=seller_name,
                seller_paypal=payment.paypal_address,
                product_id = product.id,
                product_name=product.name,
                product_description=product.description,
                product_short_description=product.short_description,
                product_category_name=category_name,
                product_image1=product.image1,
                product_image2=product.image2,
                product_image3=product.image3,
                product_price=product.price,
                product_sale_price=product.sale_price,
                product_tax_status=product.tax_status,
                product_tax_class=product.tax_class,
                currency="$",
                quantity=quantity,
                first_name=first_name,
                last_name=last_name,
                country=country,
                address=address,
                state=state,
                city=city,
                postcode=postcode,
                phone=phone,
                email=email,
                total_cost=total_cost,
                total_tax=total_tax
            )
            order.save()


            cart_item = Cart.objects.get(product_id=product.id)
            cart_item.delete()

        admin = UserDatabase.objects.get(user_type="ADMIN")
        admin_email = admin.email
        seller = UserDatabase.objects.get(id=seller_id)
        seller_email = seller.email
        send_mail(
            'New Orders on ehomespun.com',
            'You have new multiple orders on ehomespun.com. Please login to check.',
            admin_email,
            [seller_email],
            fail_silently=False,
        )

    return redirect("shopPage")