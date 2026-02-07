# cart/views.py
import json
import logging
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from apps.main.models import Product
from apps.cart.cart import Cart
from .models import Order, OrderItem
from .liqpay_utils import LiqPayAPI



def checkout(request):
    """
    Страница подтверждения заказа (checkout).
    Создаёт Order и отображает форму оплаты LiqPay.
    """
    cart = Cart(request)

    if len(cart) == 0:
        messages.info(request, 'Кошик порожній.')
        return redirect('cart:cart_detail')

    # Генерируем уникальный order_id
    order_id = f'ORDER-{uuid.uuid4().hex[:12].upper()}'

    # Создаём заказ со статусом pending
    subtotal = str(cart.get_subtotal())
    discount = str(cart.get_discount())
    total = str(cart.get_total_price())

    order = Order.objects.create(
        order_id=order_id,
        subtotal=subtotal,
        discount=discount,
        total=total,
        status='pending',
    )

    # Создаём позиции заказа
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            product_name=item['product'].name,
            quantity=item['quantity'],
            unit_price=item['price'],
        )

    # Сохраняем order_id в сессии для callback
    request.session['pending_order_id'] = order_id

    # Готовим данные для формы LiqPay
    liqpay = LiqPayAPI()

    # URL для возврата пользователя после оплаты
    result_url = request.build_absolute_uri(reverse('payments:liqpay_success'))

    # URL для серверного callback
    server_url = request.build_absolute_uri(reverse('payments:liqpay_callback'))

    # Описание платежа
    description = f'Оплата замовлення {order_id} на BulavaArms'

    # Генерируем data и signature
    payment_data = liqpay.create_payment_form(
        order_id=order_id,
        amount=str(total),
        description=description,
        result_url=result_url,
        server_url=server_url,
    )

    # Подготовка данных для шаблона
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


@csrf_exempt
@require_POST
def liqpay_callback(request):
    """
    Server callback от LiqPay (асинхронное уведомление).
    Обновляет статус заказа после оплаты.
    """
    data = request.POST.get('data')
    signature = request.POST.get('signature')

    if not data or not signature:
        logger.warning('LiqPay callback: missing data or signature')
        return HttpResponse(status=400)

    liqpay = LiqPayAPI()
    callback_data = liqpay.verify_callback(data, signature)

    if not callback_data:
        logger.error('LiqPay callback: invalid signature')
        return HttpResponse(status=400)

    logger.info(f'LiqPay callback received: {callback_data}')

    # Извлекаем данные
    order_id = callback_data.get('order_id')
    status = callback_data.get('status')
    payment_id = callback_data.get('payment_id')
    liqpay_order_id = callback_data.get('liqpay_order_id')

    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        logger.error(f'LiqPay callback: order {order_id} not found')
        return HttpResponse(status=404)

    # Обновляем заказ
    order.liqpay_payment_id = payment_id or ''
    order.liqpay_order_id = liqpay_order_id or ''

    # Маппинг статусов LiqPay → наши статусы
    status_map = {
        'success': 'paid',  # оплачено
        'failure': 'cancelled',  # ошибка
        'reversed': 'refunded',  # возврат
        'sandbox': 'paid',  # тестовая оплата (sandbox)
        'processing': 'processing',  # в обработке
    }

    order.status = status_map.get(status, 'pending')
    order.save()

    logger.info(f'Order {order_id} updated: status={order.status}')

    return HttpResponse('OK', status=200)


def liqpay_success(request):
    """
    Страница успешной оплаты (result_url).
    LiqPay редиректит сюда пользователя после оплаты.
    """
    order_id = request.session.get('pending_order_id')

    if not order_id:
        messages.error(request, 'Замовлення не знайдено.')
        return redirect('cart:cart_detail')

    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, 'Замовлення не знайдено.')
        return redirect('cart:cart_detail')

    # Очищаем корзину если оплата успешна или в обработке
    if order.status in ['paid', 'processing']:
        cart = Cart(request)
        if cart.has_products():
            cart.clear()

    # Удаляем pending_order_id из сессии
    request.session.pop('pending_order_id', None)

    context = {
        'order': order,
    }

    return render(request, 'payments/success.html', context)


def liqpay_cancel(request):
    """
    Страница отмены оплаты (опционально).
    Можно использовать если пользователь закрыл окно LiqPay.
    """
    # Удаляем pending_order_id из сессии
    order_id = request.session.pop('pending_order_id', None)

    if order_id:
        # Опционально: отменяем заказ
        try:
            order = Order.objects.get(order_id=order_id)
            if order.status == 'pending':
                order.status = 'cancelled'
                order.save()
        except Order.DoesNotExist:
            pass

    return render(request, 'payments/cancel.html')