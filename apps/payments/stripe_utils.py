import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(request, cart):
    """
    Создаёт Stripe Checkout Session из текущей корзины.

    Возвращает объект session со ссsesionId для редиректа.
    """
    domain = request.build_absolute_uri('/')[:-1]  # http://localhost:8000

    line_items = []

    for item in cart:
        product = item['product']
        price_in_cents = int(item['price'] * 100)

        line_items.append({
            'price_data': {
                'currency': settings.STRIPE_CURRENCY,
                'product_data': {
                    'name': product.name,
                    'description': product.description[:255] if product.description else '',
                },
                'unit_price': price_in_cents,
            },
            'quantity': item['quantity'],
        })

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=line_items,
            success_url=domain + reverse('cart:stripe_success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain + reverse('cart:stripe_cancel'),
            customer_email=None,
            metadata={
                'cart': str({
                    str(item['product'].id): {
                        'name': item['product'].name,
                        'quantity': item['quantity'],
                        'price': str(item['price']),
                    }
                    for item in cart
                }),
            },
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f'Ошибка Stripe: {str(e)}')