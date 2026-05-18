# apps/wishlist/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from apps.main.models import Product
from .models import Wishlist, WishlistItem


@login_required
def wishlist_view(request):
    """Відображення списку бажань користувача"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product').order_by('-added_at')

    context = {
        'wishlist': wishlist,
        'items': items,
        'items_count': items.count(),
    }
    return render(request, 'wishlist/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Додати товар до списку бажань"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    # Перевірити чи товар вже у списку
    if wishlist.items.filter(product=product).exists():
        return JsonResponse({
            'success': False,
            'message': 'Товар вже у вашому списку бажань'
        })

    wishlist.add_product(product)

    # Повідомлення для AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} додано до списку бажань',
            'wishlist_count': wishlist.get_products_count()
        })

    messages.success(request, f'{product.name} додано до списку бажань')
    return redirect('wishlist:wishlist_detail')


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Видалити товар зі списку бажань"""
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)

    removed = wishlist.remove_product(product)

    # Повідомлення для AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} видалено зі списку',
            'wishlist_count': wishlist.get_products_count()
        })

    if removed:
        messages.success(request, f'{product.name} видалено зі списку')
    return redirect('wishlist:wishlist_detail')


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    """Додати або видалити товар (переключити)"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    removed, added = wishlist.toggle_product(product)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if added:
            message = f'{product.name} додано до списку бажань'
        else:
            message = f'{product.name} видалено зі списку'

        return JsonResponse({
            'success': True,
            'message': message,
            'in_wishlist': added,
            'wishlist_count': wishlist.get_products_count()
        })

    return redirect('wishlist:wishlist_detail')


@login_required
def wishlist_clear(request):
    """Очистити весь список бажань"""
    wishlist = get_object_or_404(Wishlist, user=request.user)

    if request.method == 'POST':
        wishlist.clear()
        messages.success(request, 'Список бажань очищений')
        return redirect('wishlist:wishlist_detail')

    return render(request, 'wishlist/confirm_clear.html', {'wishlist': wishlist})


@login_required
def check_in_wishlist(request, product_id):
    """Перевірити чи товар у списку (для AJAX)"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    in_wishlist = wishlist.has_product(product)

    return JsonResponse({
        'in_wishlist': in_wishlist,
        'wishlist_count': wishlist.get_products_count()
    })