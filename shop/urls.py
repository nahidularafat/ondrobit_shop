from django.urls import path
from . import views

urlpatterns = [
    # এটি আপনার লগইন পেজ (যেটি মূল লিংকে ওপেন হবে)
    path('login/', views.login_view, name='login'), 
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]