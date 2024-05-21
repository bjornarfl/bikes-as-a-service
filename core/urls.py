from django.urls import path
from . import views

urlpatterns = [
    path('populate/', views.populate_profile, name="core-populate-profile"),
    path('fullreset/', views.full_reset, name="core-fullreset")
]