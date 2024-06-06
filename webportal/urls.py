from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('bikemap/', views.bikemap, name='webportal-bikemap'),
    path('register/', views.register, name="webportal-register"),
    path('profile/<int:pk>/', views.profile, name="webportal-profile"),
    path('profile/receipt/', views.get_receipt, name="webportal-receipt"),
    path('profile/subscription/', views.updateSubscription, name="webportal-subscription"),
    path('profile/payment/', views.paymentInfo, name="webportal-payment"),
    path('profile/payment/delete/<int:pk>/', views.deletePaymentInfo, name="webportal-payment-delete"),
    path('profile/bikerental/<int:pk>/', views.bikeRentalDetail, name="webportal-bikerental-detail"),

    #Default login and logout handlers from Django
    path('login/', auth_views.LoginView.as_view(template_name='webportal/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),

    path('', views.home, name='webportal-home')    
]