from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('liqpay/callback/', views.liqpay_callback, name='liqpay_callback'),
    path('liqpay/success/', views.liqpay_success, name='liqpay_success'),
    path('liqpay/cancel/', views.liqpay_cancel, name='liqpay_cancel')]
