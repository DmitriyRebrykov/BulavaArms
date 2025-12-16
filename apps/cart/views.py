# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.main.models import Product
from .cart import Cart


def cart_view(request):
    """
    Відображення корзини
    """
    cart = Cart(request)
    
    # Підготовка даних для шаблону
    cart_items = []
    for item in cart:
        cart_items.append({
            'product': item['product'],
            'quantity': item['quantity'],
            'price': item['price'],
            'total_price': item['total_price'],
        })
    
    context = {
        'cart_items': cart_items,
        'cart_items_count': len(cart),
        'cart_subtotal': cart.get_subtotal(),
        'cart_discount': cart.get_discount(),
        'cart_total': cart.get_total_price(),
    }
    
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def cart_add(request, product_id):
    """
    Додати товар до корзини
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Перевірка наявності товару
    if not product.in_stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Товар відсутній на складі'
            })
        messages.error(request, 'Товар відсутній на складі')
        return redirect('main:catalog')
    
    # Отримати кількість з POST
    quantity = int(request.POST.get('quantity', 1))
    
    # Додати до корзини
    cart.add(product=product, quantity=quantity)
    
    # Відповідь для AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} додано до кошика',
            'cart_items_count': len(cart)
        })
    
    messages.success(request, f'{product.name} додано до кошика')
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """
    Видалити товар з корзини
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    cart.remove(product)
    
    # Відповідь для AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} видалено з кошика',
            'cart_items_count': len(cart),
            'cart_total': float(cart.get_total_price())
        })
    
    messages.success(request, f'{product.name} видалено з кошика')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """
    Оновити кількість товару в корзині
    """
    cart = Cart(request)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1 or quantity > 99:
            # Для AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Неправильна кількість'
                })
            # Для звичайної форми
            messages.error(request, 'Неправильна кількість')
            return redirect('cart:cart_detail')
        
        # Перевірка наявності на складі
        product = get_object_or_404(Product, id=product_id)
        if not product.in_stock and quantity > 0:
            # Для AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Товар відсутній на складі'
                })
            # Для звичайної форми
            messages.error(request, 'Товар відсутній на складі')
            return redirect('cart:cart_detail')
        
        cart.update_quantity(product_id, quantity)
        
        # Відповідь для AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Кількість оновлено',
                'cart_items_count': len(cart),
                'cart_total': float(cart.get_total_price())
            })
        
        # Для звичайної форми - редірект назад на корзину
        messages.success(request, 'Кількість оновлено')
        return redirect('cart:cart_detail')
        
    except (ValueError, TypeError):
        # Для AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Помилка обробки запиту'
            })
        # Для звичайної форми
        messages.error(request, 'Помилка обробки запиту')
        return redirect('cart:cart_detail')


def cart_clear(request):
    """
    Очистити корзину
    """
    cart = Cart(request)
    cart.clear()
    
    messages.success(request, 'Корзину очищено')
    return redirect('cart:cart_detail')