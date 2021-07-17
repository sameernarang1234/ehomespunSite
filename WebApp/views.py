from django.shortcuts import render
from .models import Category, SubCategory

# Create your views here.
def homePage(request):
    categories = Category.objects.all()
    params = {
        "categories": categories
    }
    return render(request, 'home.html', params)

def loginPage(request):
    return render(request, 'login.html')

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