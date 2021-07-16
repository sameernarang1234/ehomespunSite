from django.shortcuts import render

# Create your views here.
def homePage(request):
    return render(request, 'home.html')

def loginPage(request):
    return render(request, 'login.html')

def supportPage(request):
    return render(request, 'support.html')

def buyerTerms(request):
    return render(request, 'buyerTerms.html')

def sellerTerms(request):
    return render(request, 'sellerTerms.html')