# cart/context_processors.py
from .cart import Cart


def cart(request):
    """
    Контекстний процесор для корзини
    Додає об'єкт корзини та кількість товарів до всіх шаблонів
    """
    cart_obj = Cart(request)
    
    return {
        'cart': cart_obj,
        'cart_items_count': len(cart_obj),
    }