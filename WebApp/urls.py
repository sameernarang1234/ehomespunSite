from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.homePage, name='homePage'),
    path('login/', views.loginPage, name='loginPage'),
    path('support/', views.supportPage, name='supportPage'),
    path('buyer-information/', views.buyerTerms, name='buyerTerms'),
    path('seller-information/', views.sellerTerms, name='sellerTerms'),
]