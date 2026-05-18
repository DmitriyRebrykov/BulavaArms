# apps/loyalty/urls.py
from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('dashboard/', views.loyalty_dashboard, name='dashboard'),
    path('transactions/', views.loyalty_transactions, name='transactions'),
    path('tiers/', views.loyalty_tiers, name='tiers'),
    path('use-points/', views.use_loyalty_points, name='use_points'),
]