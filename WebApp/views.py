from django.shortcuts import render, redirect
from .models import Category, SubCategory, UserDatabase, Product, StoreState, Order, Store, SellerPaymentDetail, Shipping
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

# Create your views here.
def homePage(request):
    categories = Category.objects.all()
    params = {
        "categories": categories
    }
    return render(request, 'home.html', params)

def loginPage(request):
    return render(request, 'login.html')

def handleSignup(request):
    if request.method == 'POST':
        inputUsername = request.POST.get('username')
        inputEmail = request.POST.get('email')
        inputPassword = request.POST.get('password')
        isMerchantAccount = request.POST.get('isMerchantAccount')

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

            if (userType == "BUYER"):
                return redirect("userDashboard")
            else:
                return redirect("proDashboard")
    return redirect("loginPage")

def loginUser(request):
    if request.method == "POST":
        inputUsername = request.POST.get("username")
        inputPassword = request.POST.get("password")
        loggedInUser = authenticate(username=inputUsername, password=inputPassword)

        if loggedInUser is not None:
            login(request, loggedInUser)
            request.session["username"] = inputUsername

            userDB = UserDatabase.objects.get(username=inputUsername)
            userType = userDB.user_type

            if userType == "MERCHANT":
                return redirect("proDashboard")
            else:
                return redirect("userDashboard")

    return redirect("loginPage")

def logoutUser(request):
    logout(request)
    return redirect("homePage")

def dashboard(request):
    username = request.session["username"]
    user = UserDatabase.objects.get(username=username)
    if user.user_type == "MERCHANT":
        return redirect("proDashboard")
    else:
        return redirect("userDashboard")

def supportPage(request):
    return render(request, 'support.html')

def buyerTerms(request):
    return render(request, 'buyerTerms.html')

def sellerTerms(request):
    return render(request, 'sellerTerms.html')

def refundPolicy(request):
    return render(request, 'refund.html')

def passwordReset(request):
    return render(request, 'passwordReset.html')

def userDashboard(request):
    return render(request, 'userDashboard.html')

def ordersPage(request):
    return render(request, 'ordersPage.html')

def subscriptionsPage(request):
    return render(request, 'subscriptionsPage.html')

def downloadsPage(request):
    return render(request, 'downloadsPage.html')

def addressPage(request):
    return render(request, 'addressPage.html')

def paymentMethodPage(request):
    return render(request, 'paymentMethodPage.html')

def accountPage(request):
    return render(request, 'accountPage.html')

def becomeSellerPage(request):
    return render(request, 'becomeSellerPage.html')

def proDashboard(request):
    username = request.session["username"]
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

    params = {
        "num_orders": num_orders,
        "amount_orders": amount_orders,
        "num_products": num_products,
        "amount_products": amount_products
    }

    return render(request, 'proDashboard.html', params)

def proProducts(request):
    user = UserDatabase.objects.get(username=request.session["username"])
    user_id = user.id
    products = Product.objects.filter(seller_id=user_id)
    params = {
        "products": products
    }
    return render(request, 'proProducts.html', params)

def addProduct(request):

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
    }
    return render(request, 'addProduct.html', params)

def proOrders(request):
    return render(request, 'proOrders.html')

def proSettings(request):
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

        settings_updated = True


    states = StoreState.objects.all()
    params = {
        "states": states,
        "settings": settings_updated
    }
    return render(request, 'proSettings.html', params)

def proPayments(request):

    paymentStatus = False

    if request.method == "POST":
        paypal_client_id = request.POST.get("paypal_client_id")
        stripe_public_key = request.POST.get("stripe_public_key")
        stripe_private_key = request.POST.get("stripe_private_key")

        payment = SellerPaymentDetail(
            paypal_client_id=paypal_client_id,
            stripe_public_key=stripe_public_key,
            stripe_private_key=stripe_private_key
        )
        payment.save()

        paymentStatus = True
    
    params = {
        "paymentStatus": paymentStatus
    }

    return render(request, 'proPayments.html', params)

def proBranding(request):
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

        store.store_banner = store_banner
        store.store_icon = store_icon

        store.save()

        images_uploaded = True

    params = {
        "images_uploaded": images_uploaded,
    }
    return render(request, 'proBranding.html', params)

def proShipping(request):
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
        
        shipping = Shipping(
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

        shipping_enabled = True
    
    params = {
        "shipping_enabled": shipping_enabled
    }

    return render(request, 'proShipping.html', params)

def categoryPage(request):
    category = request.GET.get('category')
    categoryDB = Category.objects.get(name=category)
    categoryID = categoryDB.id

    subCategories = SubCategory.objects.filter(category_id=categoryID)

    params = {
        'sub_categories': subCategories,
        'category': category
    }
    return render(request, 'categoryPage.html', params)