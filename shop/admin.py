from django.contrib import admin

# Register your models here.
from .models import category, Product, cart, CartItem, Order, Rating, orderItem


# @admin.register(category)
# class categoryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'slug']
#     prepopulated_fields = {'slug': ('name',)}
