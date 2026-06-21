from .models import cart

def cart_items_count(request):
    if request.user.is_authenticated:
        try:
            cart_obj = cart.objects.get(user=request.user)
            return {'cart_items_count': cart_obj.get_total_items()}
        except cart.DoesNotExist:
            return {'cart_items_count': 0}
    return {'cart_items_count': 0}