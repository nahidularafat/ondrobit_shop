from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100,  unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = ' Categories'
        
    def __str__(self):
        return self.name
class Product(models.Model):
    # ... আপনার আগের সব ফিল্ড থাকবে ...
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # এটি আসল দাম (Original Price)
    stock = models.PositiveBigIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)   
    updated = models.DateTimeField(auto_now=True)   
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True)
    
    # ১. ডিসকাউন্ট পার্সেন্টেজ ফিল্ড (যদি অলরেডি মাইগ্রেশন করা থাকে তবে ঠিক আছে, না থাকলে এটি লিখুন)
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return self.name
        
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / ratings.count()
        return 0

    # ২. ডিসকাউন্ট বাদ দিয়ে বর্তমান বিক্রয়মূল্য বের করার প্রোপার্টি
    @property
    def discounted_price(self):
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price
    
class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return self.user.username + ' - ' + str(self.rating)

class cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username + ' Cart'
        
    def get_total_price(self):
        total = sum(item.get_cost() for item in self.items.all())
        return total   
        
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())
class CartItem(models.Model):
    cart = models.ForeignKey(cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'  

    # ৩. কার্ট আইটেমের খরচ আসল দামের বদলে ডিসকাউন্টেড প্রাইস দিয়ে গুণ হবে
    def get_cost(self):
        return self.product.discounted_price * self.quantity
    
      
# নতুন মডেল: অ্যাডমিন এখান থেকে ডেলিভারি এরিয়া এবং চার্জ অ্যাড করবে
class ShippingZone(models.Model):
    name = models.CharField(max_length=100)  # যেমন: Inside Dhaka
    charge = models.DecimalField(max_digits=10, decimal_places=2) # যেমন: 80.00

    def __str__(self):
        return f"{self.name} (৳{self.charge})"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Failed', 'Failed'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('SSLCOMMERZ', 'Online Payment (SSLCommerz)'),
    ) # নতুন অপশন
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15, default="") # নতুন ফিল্ড
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD') # নতুন ফিল্ড
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    note = models.TextField(blank=True, null=True)
    paid = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    shipping_zone_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    
    def __str__(self):
        return f'Order {self.id} by {self.user.username}' 

    class Meta:
        ordering = ['-created']   
        
    def get_total_cost(self):
           
            total_items_cost = sum(item.get_cost() for item in self.items.all())
            return total_items_cost + self.shipping_cost                

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}' 

    def get_cost(self):
        return self.price * self.quantity