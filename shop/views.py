from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from .models import Product, category, cart, CartItem, Order, Rating
from .froms import ResgistrationForm, LoginForm, CartItemForm, OrderForm
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Check database for the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, '', {'error': 'Invalid credentials'})
    return render(request, '')

def register_view(request):
    if request.method == 'POST':
        form = ResgistrationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('home')
        
def logout_view(request):
    logout(request)
    return redirect('home')            