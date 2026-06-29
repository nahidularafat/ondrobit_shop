from django.contrib import admin
from .models import category, Product, cart, CartItem, Order, Rating, OrderItem, ShippingZone, ProductImage, ProductSpecification

admin.site.site_header = "My Shop Admin"
admin.site.site_title = "Shop Dashboard"
admin.site.index_title = "Welcome to Shop Panel"

# --- Inlines ---
class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 4

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']

# --- Registrations ---

@admin.register(category)
class categoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'stock', 'created', 'updated']
    list_filter = ['category', 'created', 'updated']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock'] 
    # এখানে সব Inline গুলো একসাথে আছে
    inlines = [RatingInline, ProductImageInline, ProductSpecificationInline]

@admin.register(cart)
class cartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    inlines = [CartItemInline]
     
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'address']
    list_filter = ['paid', 'created', 'status']
    search_fields = ['first_name', 'last_name', 'email', 'address']
    inlines = [OrderItemInline]

@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'charge']
    list_editable = ['charge']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'comment', 'created']
    list_filter = ['rating', 'created']
    search_fields = ['product__name', 'user__username', 'comment']