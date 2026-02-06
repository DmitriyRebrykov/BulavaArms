# cart/context_processors.py
from .cart import Cart


def cart(request):
    cart_obj = Cart(request)
    
    return {
        'cart': cart_obj,
        'cart_items_count': len(cart_obj),
    }