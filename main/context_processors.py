from .models import CartItem

def cart_data(request):
    if request.user.is_authenticated:
        cart_goods = CartItem.objects.filter(user=request.user)
        cart_total = sum(item.product.price * item.quantity for item in cart_goods)
        cart_count = sum(item.quantity for item in cart_goods)
    else:
        cart_goods = []
        cart_total = 0
        cart_count = 0

    return {
        'cart_goods': cart_goods,
        'cart_total': cart_total,
        'cart_count': cart_count,
    }