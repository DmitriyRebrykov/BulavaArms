# apps/loyalty/urls.py
from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('use-points/', views.use_loyalty_points, name='use_points'),
]