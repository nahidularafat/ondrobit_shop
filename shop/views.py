from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# আপনার মডেলগুলো
from .models import Product, category, cart, CartItem, Order, Rating

# ফর্মগুলো
from .forms import RegistrationForm, RatingForm, CheckoutForm
from django. db.models import Q,Min,Max,Avg

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # 'home' এর বদলে 'login' দেওয়া হলো
            return redirect('login') 
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid credentials'})
            
    return render(request, 'shop/login.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('register') 
    else:
        form = RegistrationForm()
        
    return render(request, 'shop/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    featured_products = 
    Product.objects.filter(available=True).order_by('-created_at')[:8]
    categories = category.objects.all()
    return render(request, 'shop/home.html', {'featured_products': featured_products, 'categories': categories})

def product_detail(request, category_slug, product_slug):
    category = None
    categories = category.objects.all()
    prodcts=Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(category, slug=category_slug)
        prodcts = prodcts.filter(category=category)
        
    min_price = prodcts.aggregate(Min('price'))['price__min']
    max_price = prodcts.aggregate(Max('price'))['price__max']    
    
    if request.Get.get('min_price'):
        products=prodcts.filter(price__gte=request.GET.get('min_price'))
    if request.Get.get('max_price'):
        products=prodcts.filter(price__lte=request.GET.get('max_price'))   
        
    if request.GET.get('rating'):
        min_rating = request.GET.get('rating')
        products = products.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__gte=min_rating) 
    
    if request.GET.get('search'):
        query = request.GET.get('search')
        products = products.filter(
            Q(name__icontains = query) | 
            Q(description__icontains = query) | 
            Q(category__name__icontains = query)  
        )
    
    return render(request, 'shop/product_list.html', {
        'category' : category,
        'categories' : categories,
        'products' : products,
        'min_price' : min_price,
        'max_price' : max_price
    })        