# cart/views.py
import json
import stripe
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from apps.main.models import Product
from .models import Order, OrderItem
from .stripe_utils import create_stripe_session
from apps.cart.cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.info(request, 'Кошик порожній.')
        return redirect('cart:cart_detail')

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
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, 'payments/checkout.html', context)

@require_POST
def stripe_checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, 'Кошик порожній.')
        return redirect('cart:cart_detail')

    try:
        session = create_stripe_session(request, cart)
        request.session['stripe_session_id'] = session.id
        return redirect(session.url)
    except Exception as e:
        messages.error(request, 'Помилка при переході до оплаті. Попробуйте ещё раз.')
        return redirect('payments:checkout')


def stripe_success(request):
    session_id = request.GET.get('session_id')

    if not session_id:
        messages.error(request, 'Невалідна сесія оплаті.')
        return redirect('cart:cart_detail')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        messages.error(request, 'Не вдалось перевірити сесію оплаті.')
        return redirect('cart:cart_detail')

    try:
        order = Order.objects.get(stripe_session_id=session_id)
    except Order.DoesNotExist:
        order = _create_order_from_session(session, request)

    cart = Cart(request)
    if cart.has_products():
        cart.clear()

    request.session.pop('stripe_session_id', None)

    context = {
        'order': order,
    }

    return render(request, 'cart/success.html', context)


def stripe_cancel(request):
    request.session.pop('stripe_session_id', None)

    return render(request, 'cart/cancel.html')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f'Webhook: невалидный payload — {e}')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f'Webhook: невалидная подпись — {e}')
        return HttpResponse(status=400)

    # ─── checkout.session.completed ───
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f'Webhook: checkout.session.completed — session_id={session["id"]}')

        # Если заказ уже существует (например, создан на success view) — обновляем статус
        try:
            order = Order.objects.get(stripe_session_id=session['id'])
            if order.status == 'pending':
                order.status = 'paid'
                order.stripe_payment_intent = session.get('payment_intent', '')
                order.save()
                logger.info(f'Webhook: updated existing order #{order.id} -> paid')
        except Order.DoesNotExist:
            # Создаём заказ из webhook (основной путь)
            order = _create_order_from_webhook(session)
            logger.info(f'Webhook: created order #{order.id}')

    # ─── payment_intent.payment_failed ───
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        logger.warning(f'Webhook: payment_intent.payment_failed — intent_id={payment_intent["id"]}')
        # Попытка найти заказ по payment_intent и отметить как cancelled
        try:
            order = Order.objects.get(stripe_payment_intent=payment_intent['id'])
            order.status = 'cancelled'
            order.save()
        except Order.DoesNotExist:
            pass  # Заказ ещё не создан — ничего не делаем

    return HttpResponse(status=200)


# ─────────────────────────────────
#  Вспомогательные функции
# ─────────────────────────────────

def _create_order_from_session(session, request):
    """
    Создаёт Order + OrderItem из Stripe Session.
    Используется как fallback на success page, если webhook ещё не обработал событие.
    """
    cart = Cart(request)

    subtotal = cart.get_subtotal()
    discount = cart.get_discount()
    total = cart.get_total_price()

    order = Order.objects.create(
        stripe_session_id=session.id,
        stripe_payment_intent=session.get('payment_intent', ''),
        email=session.get('customer_details', {}).get('email', '') or '',
        subtotal=subtotal,
        discount=discount,
        total=total,
        status='paid' if session.get('payment_status') == 'paid' else 'pending',
    )

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            product_name=item['product'].name,
            quantity=item['quantity'],
            unit_price=item['price'],
        )

    return order


def _create_order_from_webhook(session):
    """
    Создаёт Order + OrderItem из данных webhook.
    metadata содержит снимок корзины в виде строки dict.
    """
    email = ''
    customer_details = session.get('customer_details')
    if customer_details:
        email = customer_details.get('email', '')

    # Парсим metadata.cart (строка Python-dict)
    cart_meta = session.get('metadata', {}).get('cart', '{}')
    try:
        import ast
        cart_data = ast.literal_eval(cart_meta)  # безопасно: только мы пишем в metadata
    except (ValueError, SyntaxError):
        cart_data = {}

    # Считаем суммы из cart_data
    subtotal_cents = 0
    total_cents = session.get('amount_total', 0)  # в минимальных единицах
    subtotal_cents = session.get('amount_subtotal', total_cents)

    subtotal = subtotal_cents / 100
    total = total_cents / 100
    discount = subtotal - total

    order = Order.objects.create(
        stripe_session_id=session['id'],
        stripe_payment_intent=session.get('payment_intent', ''),
        email=email,
        subtotal=subtotal,
        discount=discount,
        total=total,
        status='paid' if session.get('payment_status') == 'paid' else 'pending',
    )

    # Создаём позиции из metadata
    for product_id_str, info in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id_str))
        except (Product.DoesNotExist, ValueError):
            product = None

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=info.get('name', 'Товар'),
            quantity=int(info.get('quantity', 1)),
            unit_price=info.get('price', '0'),
        )

    return order