from django.shortcuts import render, redirect
from .models import Category, SubCategory, UserDatabase, Product, StoreCity
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

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
    return render(request, 'proDashboard.html')

def proProducts(request):
    user = UserDatabase.objects.get(username=request.session["username"])
    user_id = user.id
    products = Product.objects.filter(seller_id=user_id)
    params = {
        "products": products
    }
    return render(request, 'proProducts.html', params)

def addProduct(request):
    categories = Category.objects.all()
    params = {
        "categories": categories
    }
    return render(request, 'addProduct.html', params)

def proOrders(request):
    return render(request, 'proOrders.html')

def proSettings(request):
    cities = StoreCity.objects.all()
    params = {
        "cities": cities
    }
    return render(request, 'proSettings.html', params)

def proPayments(request):
    return render(request, 'proPayments.html')

def proBranding(request):
    return render(request, 'proBranding.html')

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