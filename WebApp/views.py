from django.shortcuts import render, redirect
from .models import Category, SubCategory, UserDatabase, Product, StoreState, Order, Store, SellerPaymentDetail, Shipping, Coupon, UserReview, UserComment, Cart, Wishlist, BuyerBillingAddress, BuyerAddress, BuyerPaymentDetail

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import date, timedelta

import stripe

# Create your views here.
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
    for product in allProducts:
        if count > 4:
            break
        products.append(product)
        count += 1
    
    print(products)
    
    params = {
        "categories": categories,
        "products": products,
        "cart_total": cart_total
    }
    return render(request, 'home.html', params)

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
                request.session.set_expiry(86400)
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

    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'support.html', params)

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
    return render(request, 'ordersPage.html', params)

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

def paymentMethodPage(request):
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

    payment_updated = False
    if request.method == "POST":
        card_number = request.POST.get("card_number")
        expiry = request.POST.get("expiry")
        cvv = request.POST.get("cvv")
        
        buyer = UserDatabase.objects.get(username=username)
        buyer_id = buyer.id

        try:
            payment = BuyerPaymentDetail.objects.get(buyer_id=buyer_id)
        except:
            payment = None

        if payment == None:
            newPayment = BuyerPaymentDetail(
                    buyer_id=buyer_id,
                    card_number=card_number,
                    expiry=expiry,
                    cvv=cvv
            )
            newPayment.save()
        else:
            payment.card_number = card_number
            payment.expiry = expiry
            payment.cvv = cvv
            payment.save()

        payment_updated = True

    categories = Category.objects.all()
    params = {
                "payment_updated": payment_updated,
                "categories": categories,
                "cart_total": cart_total
            }

    return render(request, 'paymentMethodPage.html', params)

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
    print("USER ID")
    print(user_id)
    
    try:
        buyerAddress = BuyerAddress.objects.get(user_id=user_id)
    except:
        return render(request, "accountPage.html")

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
    categories = Category.objects.all()
    params = {
        "categories": categories,
        "cart_total": cart_total
    }
    return render(request, 'becomeSellerPage.html', params)

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
    
    categories = Category.objects.all()
    params = {
        "products": products,
        "next_page": next_page,
        "prev_page": prev_page,
        "categories": categories,
        "cart_total": cart_total
    }

    return render(request, 'proProducts.html', params)

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

def proOrders(request):
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
    return render(request, 'proOrders.html', params)

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
        paypal_client_id = request.POST.get("paypal_client_id")
        stripe_public_key = request.POST.get("stripe_public_key")
        stripe_private_key = request.POST.get("stripe_private_key")

        try:
            prevPayment = SellerPaymentDetail.objects.get(seller_id=seller_id)
        except:
            prevPayment = None

        if prevPayment is None:
            payment = SellerPaymentDetail(
                seller_id = seller_id,
                paypal_client_id=paypal_client_id,
                stripe_public_key=stripe_public_key,
                stripe_private_key=stripe_private_key
            )
            payment.save()
        else:
            if paypal_client_id != "":
                prevPayment.paypal_client_id = paypal_client_id

            if stripe_public_key != "":
                prevPayment.stripe_public_key = stripe_public_key

            if stripe_private_key != "":
                prevPayment.stripe_private_key = stripe_private_key

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

    is_member = False
    username = request.session["username"]
    user = UserDatabase.objects.get(username=username)
    seller_id = user.id
    print("SELLER ID")
    print(seller_id)
    try:
        store = Store.objects.get(seller_id=seller_id)
    except:
        store = None

    if request.method == "POST":
        membership_type = request.POST.get("membership-type")

        store.membership_type = membership_type
        store.membership_status = "active"
        store.membership_start_date = date.today()

        store.save()

        is_member = True

    products = Product.objects.filter(seller_id=seller_id)
    product_count = 0
    for product in products:
        product_count += 1
    
    categories = Category.objects.all()

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
            "is_member": is_member,
            "membership_type": store.membership_type,
            "membership_status": store.membership_status,
            "start_date": store.membership_start_date,
            "product_count": product_count,
            "categories": categories,
            "cart_total": cart_total,
        }
    else:
        params = {
            "is_member": is_member,
            "product_count": product_count,
            "categories": categories,
            "cart_total": cart_total
        }

    return render(request,"proMembership.html", params)

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

def proRefunds(request):
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
    return render(request,"proRefunds.html", params)

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
            qty += 1
            presentCart.product_quantity = qty
            presentCart.save()

    return redirect("cartPage")

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

def checkout(request):
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
    
    quantity = int(request.POST.get("quantity"))
    product_id = request.POST.get("product_id")
    product = Product.objects.get(id=product_id)
    price = float(product.sale_price)

    amount = float(quantity) * price
    amount_int = int(amount)*100

    seller_id = product.seller_id
    sellerPaymentDetails = SellerPaymentDetail.objects.get(seller_id=seller_id)

    stripe.api_key = sellerPaymentDetails.stripe_private_key

    key = sellerPaymentDetails.stripe_public_key

    params = {
        "amount": amount_int,
        "key": key,
        "product": product,
        "quantity": quantity,
        "cart_total": cart_total
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

    amount = request.POST.get("amount")
    charge = stripe.Charge.create(
        amount=amount,
        currency="inr",
        description="Payment Gateway",
        source=request.POST["stripeToken"]
    )
    params = {
        "cart_total": cart_total
    }
    return render(request,"charge.html", params)
