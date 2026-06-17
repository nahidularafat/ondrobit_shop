from django.contrib import admin
from django.contrib import admin

admin.site.site_header = "My Shop Admin"
admin.site.site_title = "Shop Dashboard"
admin.site.index_title = "Welcome to Shop Panel"


# Register your models here.
from .models import category, Product, cart, CartItem, Order, Rating, OrderItem


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