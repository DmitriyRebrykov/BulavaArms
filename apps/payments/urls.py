# cart/urls.py
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/stripe/', views.stripe_checkout, name='stripe_checkout'),
    path('stripe/success/', views.stripe_success, name='stripe_success'),
    path('stripe/cancel/', views.stripe_cancel, name='stripe_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]