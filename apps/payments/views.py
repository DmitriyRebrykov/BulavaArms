# payments/views.py
import json
import uuid

import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from apps.cart.cart import Cart
from .models import Order, OrderItem
from .liqpay_utils import LiqPayAPI
import logging

logger = logging.getLogger(__name__)


def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.info(request, 'Кошик порожній.')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(order_id=order_id)
            order.email = request.POST.get('email', '')
            order.phone = request.POST.get('phone', '')
            order.first_name = request.POST.get('first_name', '')
            order.last_name = request.POST.get('last_name', '')
            order.city = request.POST.get('city', '')
            order.postal_code = request.POST.get('postal_code', '')
            order.address = request.POST.get('address', '')
            order.delivery_notes = request.POST.get('delivery_notes', '')
            order.save()
            return HttpResponse(status=200)
        except Order.DoesNotExist:
            return HttpResponse(status=404)

    # GET
    order_id = f'ORDER-{uuid.uuid4().hex[:12].upper()}'

    subtotal = str(cart.get_subtotal())
    discount = str(cart.get_discount())
    total = str(cart.get_total_price())

    # ← Привязываем заказ к пользователю
    order = Order.objects.create(
        order_id=order_id,
        subtotal=subtotal,
        discount=discount,
        total=total,
        status='pending',
        user=request.user if request.user.is_authenticated else None,
    )

    if request.user.is_authenticated:
        order.email = request.user.email
        order.phone = request.user.phone or ''
        order.first_name = request.user.first_name
        order.last_name = request.user.last_name
        order.city = request.user.city or ''
        order.postal_code = request.user.postal_code or ''
        order.address = request.user.address or ''
        order.save()

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            product_name=item['product'].name,
            quantity=item['quantity'],
            unit_price=item['price'],
        )

    request.session['pending_order_id'] = order_id

    liqpay = LiqPayAPI()
    result_url = request.build_absolute_uri(reverse('payments:liqpay_success'))
    server_url = request.build_absolute_uri(reverse('payments:liqpay_callback'))
    description = f'Оплата замовлення {order_id} на BulavaArms'

    payment_data = liqpay.create_payment_form(
        order_id=order_id,
        amount=str(total),
        description=description,
        result_url=result_url,
        server_url=server_url,
    )

    cart_items = []
    for item in cart:
        cart_items.append({
            'product': item['product'],
            'quantity': item['quantity'],
            'price': item['price'],
            'total_price': item['total_price'],
        })

    context = {
        'order': order,
        'cart_items': cart_items,
        'cart_items_count': len(cart),
        'cart_subtotal': subtotal,
        'cart_discount': discount,
        'cart_total': total,
        'liqpay_data': payment_data['data'],
        'liqpay_signature': payment_data['signature'],
        'liqpay_action_url': 'https://www.liqpay.ua/api/3/checkout',
    }

    return render(request, 'payments/checkout.html', context)


@require_http_methods(["POST"])
def get_nova_poshta_cities(request):
    try:
        data = json.loads(request.body)
        city_name = data.get('city_name', '')

        if not city_name or len(city_name) < 2:
            return JsonResponse({'success': False, 'error': 'Введіть мінімум 2 символи'})

        api_key = settings.NOVA_POST_KEY
        url = 'https://api.novaposhta.ua/v2.0/json/'

        payload = {
            "apiKey": api_key,
            "modelName": "Address",
            "calledMethod": "searchSettlements",
            "methodProperties": {
                "CityName": city_name,
                "Limit": "10"
            }
        }

        response = requests.post(url, json=payload, timeout=10)
        result = response.json()

        if result.get('success'):
            cities = []
            addresses = result.get('data', [])
            if addresses and len(addresses) > 0:
                addresses_list = addresses[0].get('Addresses', [])
                for address in addresses_list:
                    cities.append({
                        'ref': address.get('DeliveryCity') or address.get('Ref'),
                        'present': address.get('Present'),
                        'main_description': address.get('MainDescription'),
                        'area': address.get('Area'),
                        'region': address.get('Region')
                    })
            return JsonResponse({'success': True, 'cities': cities})
        else:
            return JsonResponse({'success': False, 'error': 'Міста не знайдено'})

    except requests.exceptions.RequestException:
        return JsonResponse({'success': False, 'error': "Помилка зв'язку з сервером Нової Пошти"})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Помилка: {str(e)}'})


@require_http_methods(["POST"])
def get_nova_poshta_warehouses(request):
    try:
        data = json.loads(request.body)
        city_ref = data.get('city_ref', '')

        if not city_ref:
            return JsonResponse({'success': False, 'error': 'Не вказано місто'})

        api_key = settings.NOVA_POST_KEY
        url = 'https://api.novaposhta.ua/v2.0/json/'

        payload = {
            "apiKey": api_key,
            "modelName": "Address",
            "calledMethod": "getWarehouses",
            "methodProperties": {
                "CityRef": city_ref,
                "Limit": "400"
            }
        }

        response = requests.post(url, json=payload, timeout=10)
        result = response.json()

        if result.get('success'):
            warehouses = []
            for warehouse in result.get('data', []):
                warehouses.append({
                    'ref': warehouse.get('Ref'),
                    'description': warehouse.get('Description'),
                    'short_address': warehouse.get('ShortAddress'),
                    'number': warehouse.get('Number'),
                    'type': warehouse.get('TypeOfWarehouse'),
                    'schedule': warehouse.get('Schedule')
                })
            return JsonResponse({'success': True, 'warehouses': warehouses})
        else:
            return JsonResponse({'success': False, 'error': 'Відділення не знайдено'})

    except requests.exceptions.RequestException:
        return JsonResponse({'success': False, 'error': "Помилка зв'язку з сервером Нової Пошти"})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Помилка: {str(e)}'})


@csrf_exempt
@require_POST
def liqpay_callback(request):
    data = request.POST.get('data')
    signature = request.POST.get('signature')

    if not data or not signature:
        return HttpResponse(status=400)

    liqpay = LiqPayAPI()
    callback_data = liqpay.verify_callback(data, signature)

    if not callback_data:
        return HttpResponse(status=400)

    order_id = callback_data.get('order_id')
    status = callback_data.get('status')
    payment_id = callback_data.get('payment_id')
    liqpay_order_id = callback_data.get('liqpay_order_id')

    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return HttpResponse(status=404)

    order.liqpay_payment_id = payment_id or ''
    order.liqpay_order_id = liqpay_order_id or ''

    status_map = {
        'success': 'paid',
        'failure': 'cancelled',
        'reversed': 'refunded',
        'sandbox': 'paid',
        'processing': 'processing',
    }
    order.status = status_map.get(status, 'pending')
    order.save()

    return HttpResponse('OK', status=200)


def liqpay_success(request):
    order_id = request.session.get('pending_order_id')

    if not order_id:
        messages.error(request, 'Замовлення не знайдено.')
        return redirect('cart:cart_detail')

    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, 'Замовлення не знайдено.')
        return redirect('cart:cart_detail')

    if order.status in ['paid', 'processing']:
        cart = Cart(request)
        if cart.has_products():
            cart.clear()

    request.session.pop('pending_order_id', None)
    return render(request, 'payments/success.html', {'order': order})


def liqpay_cancel(request):
    order_id = request.session.pop('pending_order_id', None)

    if order_id:
        try:
            order = Order.objects.get(order_id=order_id)
            if order.status == 'pending':
                order.status = 'cancelled'
                order.save()
        except Order.DoesNotExist:
            pass

    return render(request, 'payments/cancel.html')