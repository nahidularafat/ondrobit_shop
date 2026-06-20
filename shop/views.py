from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .sslcommerz import generate_sslcommerz_payment, send_order_confirmation_email

# আপনার মডেলগুলো
from .models import Product, category, cart, CartItem, Order, Rating
from.django.views.decorators.csrf import csrf_exempt
# ফর্মগুলো
from .forms import RegistrationForm, RatingForm, CheckoutForm
from django. db.models import Q,Min,Max,Avg
from .utils import generate_sslcommerz_payment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, RatingForm, CheckoutForm
from .models import Category, Product, Cart, CartItem, Rating, Order, OrderItem
from django.db.models import Q, Min, Max, Avg
from django.contrib.auth.decorators import login_required
from .sslcommerz import generate_sslcommerz_payment, send_order_confirmation_email
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

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
    featured_products = Product.objects.filter(available=True).order_by('-created_at')[:8] # descending order
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
    
    
def product_detail(request, slug):
    product = get_object_or_404(Product, slug = slug, available = True)
    related_products = Product.objects.filter(category = product.category).exclude(id=product.id)
    
    user_rating = None 
    
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(product=product, user=request.user)
        except Rating.DoesNotExist:
            pass 
        
    rating_form = RatingForm(instance=user_rating)
    
    return render(request, 'shop/product_detail.html', {
        'product' :product,
        'related_products' : related_products,
        'user_rating' : user_rating,
        'rating_form' : rating_form
    })

@login_required
def cart_detail(request):
   
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    return render(request, 'shop/cart.html', {'cart' : cart})

# cart add
@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)

   
    try: # ekahne error aste pare
        cart = Cart.objects.get(user=request.user)
    
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()
        
    # item cart e nai
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity = 1)
    
    messages.success(request, f"{product.name} has been added to your cart!")
    return redirect('product_detail', slug=product.slug)
    

def cart_update(request, product_id):
   
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    
    quantity = int(request.POST.get('quantity', 1))
    
  
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, f"{product.name} has been removed from your cart!")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"Cart updated successfully!!")
    return redirect('cart_detail') 

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.warning(request, "Your cart is empty. Please add items to checkout.")
            return redirect('cart_detail')
    except Cart.DoesNotExist:
        messages.warning(request, "Your cart is empty. Please add items to checkout.")
        return redirect('cart_detail')
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order=form.save(commit=False)
            order.user=request.user
            order.save()
            
            for item in cart.items.all():
                 OrderItem.objects.create(
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            cart.items.all().delete()
            messages.success(request, "Your order has been placed successfully!")  
            request.session['order_id'] = order.id
            return redirect('') 
        else:
            initial_data = {}
            if request.user.first_name:
                initial_data['first_name'] = request.user.first_name
            if request.user.last_name:
                initial_data['last_name'] = request.user.last_name  
                
            form = CheckoutForm(initial=initial_data)
           
        return render(request, 'shop/checkout.html', {'form': form, 'cart': cart}) 
    
    
@csrf_exempt
@login_required
def payment_process(request):
    # session 
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    payment_data = generate_sslcommerz_payment(request, order)
    
    if payment_data['status'] == 'SUCCESS':
        return redirect(payment_data['GatewayPageURL'])
    else:
        messages.error(request, 'Payment gateway error. Please Try again.')
        return redirect('checkout')
        
       
# 1. Payment Success
@csrf_exempt
@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id= order_id, user=request.user)
    # order ta paid
    # order er status --> processing
    # product er stock komiye dibo
    # transaction id
    order.paid = True 
    order.status = 'processing'
    order.transaction_id = order.id 
    order.save()
    order_items = order.order_items.all()
    for item in order_items:
        product = item.product
        product.stock -= item.quantity
        
        # 40 - 60 = -20
        if product.stock < 0:
            product.stock = 0
        product.save()
    
    # send confirmation email
    send_order_confirmation_email(order)
    
    messages.success(request, 'Payment successful')
    return render(request, 'shop/payment_success.html', {'order' : order})


@csrf_exempt
@login_required
def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id= order_id, user=request.user)
    order.status = 'canceled'
    order.save()
    return redirect('checkout')
