from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Min, Max, Avg

# আপনার মডেলগুলো 
try:
    from .models import Category, Product, cart, CartItem, Order, OrderItem, Rating
    category = Category
except ImportError:
    from .models import category, Product, cart, CartItem, Order, OrderItem, Rating
    Category = category

# ফর্মগুলো
from .forms import RegistrationForm, RatingForm, CheckoutForm

# ইউটিলিটি ফাংশনগুলো
from .utils import generate_sslcommerz_payment, send_order_confirmation_email


# --- Authentication Views ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('home')
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid credentials'})
            
    return render(request, 'shop/login.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend') 
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('home') 
    else:
        form = RegistrationForm()
        
    return render(request, 'shop/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# --- Home & Product Views ---
def home(request):
    categories = Category.objects.all()
    
    # লেটেস্ট বা ফিচারড প্রোডাক্ট
    featured_products = Product.objects.all().order_by('-id')[:5] 
    
    # ডিসকাউন্ট যুক্ত প্রোডাক্ট কুয়েরি 
    discounted_products = Product.objects.filter(
        discount_percentage__gt=0
    ).order_by('-id')[:5]

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'discounted_products': discounted_products,
    }
    return render(request, 'shop/home.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)
    
    user_rating = None 
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(product=product, user=request.user)
        except Rating.DoesNotExist:
            pass 
        
    rating_form = RatingForm(instance=user_rating)
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'user_rating': user_rating,
        'rating_form': rating_form
    })


def product_list(request, category_slug=None):
    selected_category = None 
    categories = Category.objects.all() 
    products = Product.objects.filter(available=True)
    
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
        
    min_price = products.aggregate(Min('price'))['price__min'] or 0
    max_price = products.aggregate(Max('price'))['price__max'] or 100000    
    
    if request.GET.get('min_price'):
        products = products.filter(price__gte=request.GET.get('min_price'))
    if request.GET.get('max_price'):
        products = products.filter(price__lte=request.GET.get('max_price'))   
        
    if request.GET.get('rating'):
        min_rating = request.GET.get('rating')
        products = products.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=min_rating) 
    
    if request.GET.get('search'):
        query = request.GET.get('search')
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query)  
        )
    
    return render(request, 'shop/product_list.html', {
        'category': selected_category, 
        'categories': categories,
        'products': products,
        'min_price': min_price,
        'max_price': max_price
    })        


@login_required
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            user_rating = Rating.objects.get(product=product, user=request.user)
            form = RatingForm(request.POST, instance=user_rating)
        except Rating.DoesNotExist:
            form = RatingForm(request.POST)

        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.product = product
            rating.save()
            messages.success(request, 'Thank you for your rating!')
        else:
            messages.error(request, 'Invalid rating submitted.')
            
    return redirect('product_detail', slug=product.slug)


# --- Cart Views ---
@login_required
def cart_detail(request):
    cart_obj, created = cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart_obj})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_obj, created = cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart_obj, 
        product=product, 
        defaults={'quantity': 0}
    )
    
    cart_item.quantity += 1
    cart_item.save()
    
    messages.success(request, f"{product.name} has been added to your cart!")
    return redirect('product_detail', slug=product.slug)


@login_required
def cart_update(request, product_id):
    cart_obj = get_object_or_404(cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart_obj, product=product)
    
    quantity = int(request.POST.get('quantity', 1))
  
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, f"{product.name} has been removed from your cart!")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Cart updated successfully!")
        
    return redirect('cart_detail') 


@login_required
def cart_remove(request, product_id):
    cart_obj = get_object_or_404(cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart_obj, product=product)
    
    cart_item.delete()
    messages.success(request, f"{product.name} has been removed from your cart.")
    return redirect('cart_detail')


# --- Checkout & Payment Views ---
@csrf_exempt
@login_required
def checkout(request):
    cart_obj, created = cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('product_list')
        
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            
            # কার্টের আইটেমগুলো অর্ডার আইটেম হিসেবে সেভ করা
            for item in cart_obj.items.all():
                # আপনার মডেলে থাকা discounted_price প্রপার্টি ব্যবহার করা হচ্ছে
                item_price = item.product.discounted_price
                
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item_price, 
                    quantity=item.quantity
                )
            
            # কার্ট খালি করা
            cart_obj.items.all().delete()
            
            # পেমেন্ট মেথড চেক করা
            if getattr(order, 'payment_method', 'COD') == 'COD':
                order.status = 'Pending'
                order.paid = False
                order.save()
                
                # স্টক কমানো
                for item in order.items.all():
                    product = item.product
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                    else:
                        product.stock = 0
                    product.save()
                
                send_order_confirmation_email(order)
                messages.success(request, 'Order placed successfully with Cash on Delivery!')
                return render(request, 'shop/payment_success.html', {'order': order})
            else:
                # অনলাইন পেমেন্ট (SSLCOMMERZ)
                response_data = generate_sslcommerz_payment(request, order)
                if response_data and response_data.get('status') == 'SUCCESS':
                    return redirect(response_data.get('GatewayPageURL'))
                else:
                    messages.error(request, "Payment gateway redirection failed. Created as COD.")
                    return render(request, 'shop/payment_success.html', {'order': order})
    else:
        form = CheckoutForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
        
    return render(request, 'shop/checkout.html', {'form': form, 'cart': cart_obj})


@csrf_exempt
@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    order.paid = True 
    order.status = 'Processing'
    order.transaction_id = order.id 
    order.save()
    
    order_items = order.items.all() 
    for item in order_items:
        product = item.product
        product.stock -= item.quantity
        if product.stock < 0:
            product.stock = 0
        product.save()
    
    send_order_confirmation_email(order)
    
    messages.success(request, 'Payment successful')
    return render(request, 'shop/payment_success.html', {'order': order})


@csrf_exempt
@login_required
def payment_fail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'Failed'
    order.save()
    messages.error(request, 'Payment failed! Please try again.')
    return redirect('checkout')


@csrf_exempt
@login_required
def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'Cancelled' 
    order.save()
    messages.warning(request, 'Payment cancelled.')
    return redirect('checkout')


# --- User Profile ---
@login_required
def profile(request):
    tab = request.GET.get('tab', 'orders')
    orders = Order.objects.filter(user=request.user).order_by('-created')
    completed_orders = orders.filter(status='Delivered')
    pending_orders = orders.exclude(status='Delivered')
    
    total_spent = sum(order.get_total_cost() for order in completed_orders)
    order_history_active = (tab == 'orders')
    
    return render(request, 'shop/profile.html', {
        'orders': orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_spent': total_spent,
        'order_history_active': order_history_active
    })